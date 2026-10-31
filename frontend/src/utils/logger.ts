/**
 * Production-ready Structured Frontend Logger for Swarna Khata Book
 * Provides namespaced, colored console output and an in-memory diagnostic buffer.
 */

export type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  namespace: string;
  message: string;
  details?: unknown;
}

const MAX_BUFFER_SIZE = 100;
const logBuffer: LogEntry[] = [];

const isDev = import.meta.env.DEV;

function formatBadge(namespace: string): string {
  return `[${namespace.toUpperCase()}]`;
}

function addToBuffer(entry: LogEntry) {
  if (logBuffer.length >= MAX_BUFFER_SIZE) {
    logBuffer.shift();
  }
  logBuffer.push(entry);
}

export const logger = {
  debug: (namespace: string, message: string, ...args: unknown[]) => {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: 'DEBUG',
      namespace,
      message,
      details: args.length > 0 ? args : undefined,
    };
    addToBuffer(entry);
    if (isDev) {
      console.debug(
        `%c${entry.timestamp.slice(11, 19)} %c${formatBadge(namespace)}%c ${message}`,
        'color: #94a3b8;',
        'background: #f1f5f9; color: #475569; font-weight: bold; border-radius: 4px; padding: 1px 4px;',
        'color: inherit;',
        ...args
      );
    }
  },

  info: (namespace: string, message: string, ...args: unknown[]) => {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: 'INFO',
      namespace,
      message,
      details: args.length > 0 ? args : undefined,
    };
    addToBuffer(entry);
    if (isDev) {
      console.info(
        `%c${entry.timestamp.slice(11, 19)} %c${formatBadge(namespace)}%c ${message}`,
        'color: #94a3b8;',
        'background: #e0f2fe; color: #0369a1; font-weight: bold; border-radius: 4px; padding: 1px 4px;',
        'color: inherit;',
        ...args
      );
    }
  },

  warn: (namespace: string, message: string, ...args: unknown[]) => {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: 'WARN',
      namespace,
      message,
      details: args.length > 0 ? args : undefined,
    };
    addToBuffer(entry);
    console.warn(
      `%c${entry.timestamp.slice(11, 19)} %c${formatBadge(namespace)}%c ${message}`,
      'color: #94a3b8;',
      'background: #fef3c7; color: #b45309; font-weight: bold; border-radius: 4px; padding: 1px 4px;',
      'color: inherit;',
      ...args
    );
  },

  error: (namespace: string, message: string, error?: unknown, ...args: unknown[]) => {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: 'ERROR',
      namespace,
      message,
      details: error || (args.length > 0 ? args : undefined),
    };
    addToBuffer(entry);
    console.error(
      `%c${entry.timestamp.slice(11, 19)} %c${formatBadge(namespace)}%c ${message}`,
      'color: #94a3b8;',
      'background: #fee2e2; color: #b91c1c; font-weight: bold; border-radius: 4px; padding: 1px 4px;',
      'color: inherit;',
      error ?? '',
      ...args
    );
  },

  /**
   * Retrieves the diagnostic log ring-buffer for troubleshooting or export.
   */
  getRecentLogs: (): readonly LogEntry[] => [...logBuffer],

  /**
   * Clears the in-memory log buffer.
   */
  clearBuffer: () => {
    logBuffer.length = 0;
  },
};
