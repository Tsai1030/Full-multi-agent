import { clsx } from "clsx";

interface GoldSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
}

export function GoldSelect({ label, error, className, children, ...props }: GoldSelectProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-xs font-medium tracking-widest text-gold-500 uppercase">
          {label}
        </label>
      )}
      <div className="relative">
        <select
          className={clsx(
            "select-mystic w-full rounded-xl px-4 py-3 text-sm",
            className
          )}
          {...props}
        >
          {children}
        </select>
        {/* Custom arrow */}
        <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gold-500 text-xs">
          ▾
        </span>
      </div>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

interface GoldInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function GoldInput({ label, error, className, ...props }: GoldInputProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-xs font-medium tracking-widest text-gold-500 uppercase">
          {label}
        </label>
      )}
      <input
        className={clsx(
          "input-mystic w-full rounded-xl px-4 py-3 text-sm",
          className
        )}
        {...props}
      />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
