import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Search,
  Camera,
  Trash2,
  Printer,
  Plus,
  CheckCircle2,
  Receipt,
  UserCheck,
  CreditCard,
  QrCode,
  X,
  Smartphone
} from 'lucide-react';
import api from '../../api/client';
import type { Product, Customer, GoldRate } from '../../types';
import toast from 'react-hot-toast';
import { Html5Qrcode } from 'html5-qrcode';
import { PosScannerConnectionModal } from './PosScannerConnectionModal';

interface CartItem {
  product: Product;
  quantity: number;
  gold_rate_per_gram: number;
  making_charge: number;
  stone_charge: number;
  unit_price: number;
  total_price: number;
}

export const POSScreen: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [goldRates, setGoldRates] = useState<Record<string, number>>({});
  const [selectedCustomerId, setSelectedCustomerId] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [cart, setCart] = useState<CartItem[]>([]);

  // Payment & deductions
  const [paymentMethod, setPaymentMethod] = useState<'cash' | 'upi' | 'card'>('upi');
  const [paidAmount, setPaidAmount] = useState<string>('');
  const [discount, setDiscount] = useState<string>('0');
  const [oldGoldWeight, setOldGoldWeight] = useState<string>('0');
  const [oldGoldRate, setOldGoldRate] = useState<string>('6500');
  const [notes, setNotes] = useState('');

  // QR Scanner state
  const [isScannerOpen, setIsScannerOpen] = useState(false);
  const scannerRef = useRef<Html5Qrcode | null>(null);

  // Completed sale info for invoice print
  const [completedSaleId, setCompletedSaleId] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Mobile QR Scanner Pairing & Real-time Sync State
  const [isMobileModalOpen, setIsMobileModalOpen] = useState(false);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(() => {
    try {
      return sessionStorage.getItem('pos_active_session_id') || null;
    } catch {
      return null;
    }
  });
  const [isMobileConnected, setIsMobileConnected] = useState(false);
  const [mobileDeviceInfo, setMobileDeviceInfo] = useState<string | null>(null);
  const posWsRef = useRef<WebSocket | null>(null);
  const pingIntervalRef = useRef<any>(null);
  const reconnectTimeoutRef = useRef<any>(null);
  const processedEventIdsRef = useRef<Set<string>>(new Set());

  // Stable refs so the WebSocket closure always reads the latest values
  // without needing to reconnect every time goldRates or addToCart changes.
  const goldRatesRef = useRef<Record<string, number>>({});
  const addToCartRef = useRef<((p: Product) => void) | null>(null);

  const updateActiveSessionId = useCallback((sessionId: string | null) => {
    setActiveSessionId(sessionId);
    try {
      if (sessionId) {
        sessionStorage.setItem('pos_active_session_id', sessionId);
      } else {
        sessionStorage.removeItem('pos_active_session_id');
      }
    } catch {
      // ignore
    }
  }, []);

  // Real-time WebSocket connection to backend when pairing session is active.
  // Maintains persistent connection with 20s heartbeat and auto-reconnect.
  useEffect(() => {
    if (!activeSessionId) {
      clearInterval(pingIntervalRef.current);
      clearTimeout(reconnectTimeoutRef.current);
      if (posWsRef.current) {
        try {
          posWsRef.current.close();
        } catch {
          // ignore
        }
        posWsRef.current = null;
      }
      setIsMobileConnected(false);
      setMobileDeviceInfo(null);
      return;
    }

    let isDisposed = false;

    const connect = async () => {
      let token = localStorage.getItem('access_token');
      if (!token) return;

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}/ws/pos/?session_id=${encodeURIComponent(
        activeSessionId
      )}&token=${encodeURIComponent(token)}`;

      if (posWsRef.current) {
        try {
          posWsRef.current.close();
        } catch {
          // ignore
        }
        posWsRef.current = null;
      }

      const socket = new WebSocket(wsUrl);
      posWsRef.current = socket;

      socket.onopen = () => {
        if (isDisposed) {
          socket.close();
          return;
        }
        console.log('[POS WS] Laptop socket connected for session', activeSessionId);
        // Start 20s heartbeat ping
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'ping' }));
          }
        }, 20000);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'connection_established') {
            setIsMobileConnected(Boolean(data.mobile_connected));
            if (data.mobile_device_info) setMobileDeviceInfo(data.mobile_device_info);
          } else if (data.type === 'mobile_status') {
            if (data.status === 'connected') {
              setIsMobileConnected(true);
              setMobileDeviceInfo(data.device_info || 'Mobile Phone');
              toast.success('Mobile Scanner Connected!', { icon: '📱' });
            } else {
              setIsMobileConnected(false);
              toast('Mobile scanner disconnected', { icon: 'ℹ️' });
            }
          } else if (data.type === 'item_scanned') {
            const { event_id, product } = data;
            // Idempotency guard against duplicate delivery
            if (event_id && processedEventIdsRef.current.has(event_id)) return;
            if (event_id) processedEventIdsRef.current.add(event_id);

            // Use stable ref — always reads latest addToCart with current goldRates
            if (addToCartRef.current) {
              addToCartRef.current(product);
            }
            toast.success(`✨ Scanned: ${product.name} (${product.sku})`, { duration: 4000 });
          } else if (data.type === 'scan_warning') {
            toast.error(data.error || 'Scanned item could not be resolved');
          } else if (data.type === 'session_revoked') {
            updateActiveSessionId(null);
            setIsMobileConnected(false);
          }
        } catch (err) {
          console.warn('[POS WS] Message parse error:', err);
        }
      };

      socket.onerror = (e) => {
        console.warn('[POS WS] WebSocket error:', e);
      };

      socket.onclose = async (e) => {
        clearInterval(pingIntervalRef.current);
        if (isDisposed) return;

        console.log('[POS WS] Socket closed, code:', e.code);

        // Auto-refresh token if 4403
        if (e.code === 4403) {
          const refresh = localStorage.getItem('refresh_token');
          if (refresh) {
            try {
              const res = await api.post('/auth/token/refresh/', { refresh });
              if (res.data?.access) {
                localStorage.setItem('access_token', res.data.access);
                clearTimeout(reconnectTimeoutRef.current);
                reconnectTimeoutRef.current = setTimeout(connect, 1000);
                return;
              }
            } catch {
              // Refresh failed
            }
          }
        }

        // Auto-reconnect after 3s if not revoked
        if (e.code !== 4404 && e.code !== 1000 && !isDisposed) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = setTimeout(connect, 3000);
        }
      };
    };

    connect();

    return () => {
      isDisposed = true;
      clearInterval(pingIntervalRef.current);
      clearTimeout(reconnectTimeoutRef.current);
      if (posWsRef.current) {
        try {
          posWsRef.current.close();
        } catch {
          // ignore
        }
        posWsRef.current = null;
      }
    };
  }, [activeSessionId, updateActiveSessionId]);



  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const [prodRes, custRes, ratesRes] = await Promise.all([
        api.get('/products/'),
        api.get('/customers/'),
        api.get('/gold-rates/current/'),
      ]);
      const prodList = prodRes.data.results || prodRes.data;
      setProducts(prodList);
      setCustomers(custRes.data.results || custRes.data);

      const rateMap: Record<string, number> = {};
      const ratesList: GoldRate[] = ratesRes.data.results || ratesRes.data;
      ratesList.forEach((r) => {
        rateMap[r.purity_name] = parseFloat(r.rate_per_gram);
      });
      // Update both state (for UI display) and the stable ref (for WS closure)
      goldRatesRef.current = rateMap;
      setGoldRates(rateMap);
    } catch {
      toast.error('Failed to load POS data');
    }
  };

  // Start QR Scanner via camera
  useEffect(() => {
    if (isScannerOpen) {
      const scanner = new Html5Qrcode('pos-qr-reader');
      scannerRef.current = scanner;
      scanner
        .start(
          { facingMode: 'environment' },
          { fps: 10, qrbox: { width: 250, height: 250 } },
          (decodedText) => {
            handleScannedQR(decodedText);
            stopScanner();
          },
          () => {}
        )
        .catch((err) => {
          console.warn('QR Scanner start error:', err);
          toast.error('Unable to open camera for QR scan');
          setIsScannerOpen(false);
        });
    }
    return () => {
      stopScanner();
    };
  }, [isScannerOpen]);

  const stopScanner = () => {
    if (scannerRef.current) {
      scannerRef.current.stop().catch(() => {}).then(() => {
        scannerRef.current = null;
        setIsScannerOpen(false);
      });
    }
  };

  const handleScannedQR = (qrData: string) => {
    try {
      const parsed = JSON.parse(qrData);
      const match = products.find((p) => p.sku === parsed.sku || p.id === parsed.id);
      if (match) {
        addToCart(match);
        toast.success(`Scanned: ${match.name}`);
      } else {
        toast.error(`Product with SKU ${parsed.sku} not found`);
      }
    } catch {
      // If it's a plain string SKU
      const match = products.find((p) => p.sku.toLowerCase() === qrData.toLowerCase());
      if (match) {
        addToCart(match);
        toast.success(`Scanned: ${match.name}`);
      } else {
        toast.error('Invalid QR code scanned');
      }
    }
  };

  // addToCart reads from goldRatesRef so it always uses the latest rates,
  // even when called from the WebSocket closure that was created earlier.
  const addToCart = useCallback((product: Product) => {
    const purityName = product.purity_name || '22KT (916)';
    // Read from the stable ref — always has the freshest rates regardless of closure age
    const currentRate = goldRatesRef.current[purityName] || goldRates[purityName] || 6830;
    const netWt = parseFloat(product.net_weight) || 0;
    const goldVal = netWt * currentRate;

    let making = 0;
    if (product.making_charge_type === 'per_gram') {
      making = (parseFloat(product.making_charge_value) || 0) * netWt;
    } else if (product.making_charge_type === 'percent') {
      making = goldVal * ((parseFloat(product.making_charge_value) || 0) / 100);
    } else {
      making = parseFloat(product.making_charge_value) || 0;
    }

    const unitPrice = Math.round((goldVal + making) * 100) / 100;

    setCart((prev) => {
      const existing = prev.find((item) => item.product.id === product.id);
      if (existing) {
        return prev.map((item) =>
          item.product.id === product.id
            ? {
                ...item,
                quantity: item.quantity + 1,
                total_price: Math.round(item.unit_price * (item.quantity + 1) * 100) / 100,
              }
            : item
        );
      }
      return [
        ...prev,
        {
          product,
          quantity: 1,
          gold_rate_per_gram: currentRate,
          making_charge: Math.round(making * 100) / 100,
          stone_charge: 0,
          unit_price: unitPrice,
          total_price: unitPrice,
        },
      ];
    });
  }, [goldRates]); // goldRates in dep array so useCallback recreates when rates load

  // Keep addToCartRef in sync so the WebSocket onmessage always calls the latest version
  useEffect(() => {
    addToCartRef.current = addToCart;
  }, [addToCart]);

  const updateQuantity = (productId: number, delta: number) => {
    setCart((prev) =>
      prev
        .map((item) => {
          if (item.product.id === productId) {
            const newQty = Math.max(1, item.quantity + delta);
            return {
              ...item,
              quantity: newQty,
              total_price: Math.round(item.unit_price * newQty * 100) / 100,
            };
          }
          return item;
        })
        .filter((item) => item.quantity > 0)
    );
  };

  const removeFromCart = (productId: number) => {
    setCart((prev) => prev.filter((item) => item.product.id !== productId));
  };

  // Financial calculations
  const subtotal = cart.reduce((acc, item) => acc + item.total_price, 0);
  const gst = Math.round(subtotal * 0.03 * 100) / 100; // 3% jewellery GST
  const cgst = Math.round((gst / 2) * 100) / 100;
  const sgst = Math.round((gst / 2) * 100) / 100;

  const oldGoldVal =
    (parseFloat(oldGoldWeight) || 0) * (parseFloat(oldGoldRate) || 0);
  const discVal = parseFloat(discount) || 0;

  const totalPayable = Math.max(0, Math.round((subtotal + gst - discVal - oldGoldVal) * 100) / 100);

  // Auto-fill paid amount if empty
  const effectivePaidAmount = paidAmount === '' ? totalPayable : parseFloat(paidAmount) || 0;

  const handleCheckout = async () => {
    if (cart.length === 0) {
      toast.error('Cart is empty. Add products to bill.');
      return;
    }

    try {
      setIsSubmitting(true);
      const payload = {
        customer_id: selectedCustomerId ? parseInt(selectedCustomerId) : null,
        items: cart.map((item) => ({
          product_id: item.product.id,
          quantity: item.quantity,
          gold_rate_per_gram: item.gold_rate_per_gram,
          making_charge: item.making_charge,
          stone_charge: item.stone_charge,
        })),
        payment: {
          method: paymentMethod,
          amount: effectivePaidAmount,
          reference: paymentMethod === 'upi' ? `UPI-${Date.now()}` : '',
        },
        discount: discVal,
        old_gold_weight: parseFloat(oldGoldWeight) || 0,
        old_gold_rate: parseFloat(oldGoldRate) || 0,
        notes,
      };

      const res = await api.post('/sales/', payload);
      const createdSale = res.data;
      setCompletedSaleId(createdSale.id);
      toast.success(`Invoice #${createdSale.invoice_number} created successfully!`);

      // Clear cart
      setCart([]);
      setPaidAmount('');
      setDiscount('0');
      setOldGoldWeight('0');
      setNotes('');
    } catch (err: any) {
      toast.error('Checkout failed. Check stock availability.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDownloadInvoice = (saleId: number) => {
    window.open(`/api/sales/${saleId}/invoice_pdf/`, '_blank');
  };

  const filteredCatalog = products.filter((p) => {
    const term = searchQuery.trim().toLowerCase();
    if (!term) return true;
    return (
      p.name.toLowerCase().includes(term) ||
      p.sku.toLowerCase().includes(term) ||
      (p.huid && p.huid.toLowerCase().includes(term))
    );
  });

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>POS Billing & Invoice</span>
            <span className="px-2.5 py-0.5 text-xs font-semibold bg-emerald-100 text-emerald-800 rounded-full">
              Live POS
            </span>
          </h1>
          <p className="text-sm text-slate-500">
            Scan QR tags with camera or search items to generate instant tax invoice
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setIsMobileModalOpen(true)}
            className={`flex items-center gap-2 px-4 py-2 font-bold text-xs rounded-xl border transition shadow-sm ${
              isMobileConnected
                ? 'bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border-emerald-300'
                : 'bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-700 hover:to-amber-600 text-white border-transparent'
            }`}
          >
            <Smartphone className="w-4 h-4" />
            <span>{isMobileConnected ? 'Mobile Scanner Active' : 'Connect Mobile QR Scanner'}</span>
            {isMobileConnected && (
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            )}
          </button>

          <button
            onClick={() => setIsScannerOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow-md transition"
          >
            <Camera className="w-4 h-4 text-amber-400" />
            <span>Laptop Camera</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Left Catalog / Search, Right Cart / Checkout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Product Selector */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs space-y-3">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Type SKU or product name to add..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
              />
            </div>

            {/* Quick Live Rates Indicator */}
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 text-xs">
              <span className="text-slate-400 font-semibold uppercase text-[10px]">Today's Rates:</span>
              {Object.entries(goldRates).map(([purity, rate]) => (
                <span
                  key={purity}
                  className="px-2 py-0.5 bg-amber-50 border border-amber-200 text-amber-900 rounded-md font-mono text-[11px]"
                >
                  <b>{purity}</b>: ₹{rate}/g
                </span>
              ))}
            </div>
          </div>

          {/* Product Items Table */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden max-h-[520px] overflow-y-auto">
            <div className="divide-y divide-slate-100">
              {filteredCatalog.map((prod) => {
                const purityName = prod.purity_name || '22KT (916)';
                const currentRate = goldRates[purityName] || 6830;
                const estValue = Math.round(parseFloat(prod.net_weight) * currentRate);

                return (
                  <div
                    key={prod.id}
                    className="p-3.5 hover:bg-amber-50/40 transition flex items-center justify-between gap-3"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-slate-100 border border-slate-200 overflow-hidden shrink-0 flex items-center justify-center">
                        {prod.photo_url ? (
                          <img
                            src={prod.photo_url}
                            alt={prod.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <QrCode className="w-6 h-6 text-slate-300" />
                        )}
                      </div>
                      <div>
                        <h4 className="font-bold text-sm text-slate-800">{prod.name}</h4>
                        <div className="flex items-center gap-2 text-xs text-slate-500 font-mono mt-0.5">
                          <span className="bg-slate-100 px-1.5 py-0.2 rounded font-semibold text-slate-700">
                            {prod.sku}
                          </span>
                          <span>•</span>
                          <span className="text-amber-800 font-medium">{purityName}</span>
                          <span>•</span>
                          <span>Net: {Number(prod.net_weight).toFixed(3)}g</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className="font-mono font-bold text-sm text-slate-900">
                          ₹{estValue.toLocaleString('en-IN')}
                        </div>
                        <div className="text-[10px] text-slate-400">+ making</div>
                      </div>
                      <button
                        onClick={() => addToCart(prod)}
                        className="p-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl shadow-xs transition"
                        title="Add to Bill"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right: Cart & Invoice Breakdown */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-slate-100">
              <h3 className="font-bold text-base text-slate-800 flex items-center gap-2">
                <Receipt className="w-4 h-4 text-amber-600" />
                <span>Current Invoice</span>
              </h3>
              <span className="text-xs font-semibold px-2 py-0.5 bg-slate-100 text-slate-700 rounded-md font-mono">
                {cart.length} items
              </span>
            </div>

            {/* Customer Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center gap-1">
                <UserCheck className="w-3.5 h-3.5 text-slate-400" />
                <span>Select Customer</span>
              </label>
              <select
                value={selectedCustomerId}
                onChange={(e) => setSelectedCustomerId(e.target.value)}
                className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden"
              >
                <option value="">Walk-in Customer</option>
                {customers.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.phone})
                  </option>
                ))}
              </select>
            </div>

            {/* Cart Items List */}
            <div className="max-h-56 overflow-y-auto divide-y divide-slate-100">
              {cart.length === 0 ? (
                <div className="text-center py-8 text-xs text-slate-400">
                  No items in invoice. Select items from left or scan QR.
                </div>
              ) : (
                cart.map((item) => (
                  <div key={item.product.id} className="py-2.5 flex items-center justify-between text-xs">
                    <div className="flex-1 pr-2">
                      <div className="font-semibold text-slate-800 line-clamp-1">
                        {item.product.name}
                      </div>
                      <div className="text-slate-400 font-mono text-[10px]">
                        {item.product.sku} | ₹{item.gold_rate_per_gram}/g + ₹{item.making_charge} mk
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <div className="flex items-center border border-slate-200 rounded-lg">
                        <button
                          onClick={() => updateQuantity(item.product.id, -1)}
                          className="px-2 py-0.5 text-slate-500 hover:bg-slate-100 font-mono"
                        >
                          -
                        </button>
                        <span className="px-2 py-0.5 font-bold font-mono text-slate-800">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => updateQuantity(item.product.id, 1)}
                          className="px-2 py-0.5 text-slate-500 hover:bg-slate-100 font-mono"
                        >
                          +
                        </button>
                      </div>

                      <div className="font-mono font-bold text-slate-900 w-20 text-right">
                        ₹{item.total_price.toLocaleString('en-IN')}
                      </div>

                      <button
                        onClick={() => removeFromCart(item.product.id)}
                        className="p-1 text-slate-400 hover:text-red-600 rounded-md"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Old Gold Exchange & Discount */}
            <div className="p-3 bg-amber-50/40 rounded-xl border border-amber-200/70 space-y-2 text-xs">
              <span className="font-bold text-amber-950 uppercase text-[10px]">Old Gold Exchange & Discount</span>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-[10px] text-slate-500 block">Old Gold Wt (g)</label>
                  <input
                    type="number"
                    step="0.001"
                    min="0"
                    placeholder="0.000"
                    value={oldGoldWeight}
                    onChange={(e) => setOldGoldWeight(e.target.value)}
                    className="w-full px-2 py-1 bg-white border border-slate-200 rounded-md font-mono"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-slate-500 block">Rate/g (₹)</label>
                  <input
                    type="number"
                    step="1"
                    value={oldGoldRate}
                    onChange={(e) => setOldGoldRate(e.target.value)}
                    className="w-full px-2 py-1 bg-white border border-slate-200 rounded-md font-mono"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-slate-500 block">Discount (₹)</label>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    value={discount}
                    onChange={(e) => setDiscount(e.target.value)}
                    className="w-full px-2 py-1 bg-white border border-slate-200 rounded-md font-mono"
                  />
                </div>
              </div>
              {oldGoldVal > 0 && (
                <div className="text-right text-[11px] font-bold text-emerald-800 font-mono">
                  Exchange Value: -₹{oldGoldVal.toLocaleString('en-IN')}
                </div>
              )}
            </div>

            {/* Invoice Bill Calculation Breakdown */}
            <div className="space-y-1.5 pt-2 border-t border-slate-100 text-xs font-mono">
              <div className="flex justify-between text-slate-600">
                <span>Subtotal (Pure Gold + Making):</span>
                <span>₹{subtotal.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>CGST (1.5%):</span>
                <span>₹{cgst.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>SGST (1.5%):</span>
                <span>₹{sgst.toLocaleString('en-IN')}</span>
              </div>
              {discVal > 0 && (
                <div className="flex justify-between text-emerald-700">
                  <span>Discount:</span>
                  <span>-₹{discVal.toLocaleString('en-IN')}</span>
                </div>
              )}
              {oldGoldVal > 0 && (
                <div className="flex justify-between text-emerald-700">
                  <span>Old Gold Exchange:</span>
                  <span>-₹{oldGoldVal.toLocaleString('en-IN')}</span>
                </div>
              )}
              <div className="flex justify-between text-base font-bold text-slate-900 pt-2 border-t border-slate-200">
                <span>Total Amount:</span>
                <span className="text-amber-800">₹{totalPayable.toLocaleString('en-IN')}</span>
              </div>
            </div>

            {/* Payment Options */}
            <div className="space-y-2 pt-2">
              <label className="block text-xs font-semibold text-slate-700">Payment Method</label>
              <div className="grid grid-cols-3 gap-2">
                {(['upi', 'cash', 'card'] as const).map((method) => (
                  <button
                    key={method}
                    type="button"
                    onClick={() => setPaymentMethod(method)}
                    className={`py-2 text-xs font-bold uppercase rounded-xl border transition ${
                      paymentMethod === method
                        ? 'bg-amber-600 text-white border-amber-600 shadow-xs'
                        : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {method}
                  </button>
                ))}
              </div>
            </div>

            {/* Checkout Action */}
            <button
              onClick={handleCheckout}
              disabled={isSubmitting || cart.length === 0}
              className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold rounded-xl shadow-md transition disabled:opacity-50"
            >
              <CreditCard className="w-5 h-5" />
              <span>{isSubmitting ? 'Processing Transaction...' : 'Complete Sale & Save'}</span>
            </button>

            {/* Quick Invoice Download for Last Sale */}
            {completedSaleId && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-semibold text-emerald-800">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Invoice ready!</span>
                </div>
                <button
                  onClick={() => handleDownloadInvoice(completedSaleId)}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-700 text-white text-xs font-bold rounded-lg hover:bg-emerald-800 transition"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print Tax Invoice PDF</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Camera QR Scanner Modal */}
      {isScannerOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
            <div className="flex justify-between items-center px-5 py-3 border-b border-slate-100">
              <h3 className="font-bold text-slate-800 text-sm">Scan Jewelry Tag QR Code</h3>
              <button onClick={stopScanner} className="p-1 rounded-full text-slate-400 hover:bg-slate-100">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-4">
              <div id="pos-qr-reader" className="w-full rounded-xl overflow-hidden" />
              <p className="text-center text-xs text-slate-500 mt-3">
                Point camera at the printed QR code tag on the jewelry piece
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Wireless Mobile Phone Scanner Pairing Modal */}
      <PosScannerConnectionModal
        isOpen={isMobileModalOpen}
        onClose={() => setIsMobileModalOpen(false)}
        activeSessionId={activeSessionId}
        isMobileConnected={isMobileConnected}
        mobileDeviceInfo={mobileDeviceInfo}
        onSessionStarted={(sessionId) => {
          updateActiveSessionId(sessionId);
        }}
        onSessionRevoked={() => {
          updateActiveSessionId(null);
          setIsMobileConnected(false);
          setMobileDeviceInfo(null);
        }}
      />
    </div>
  );
};
