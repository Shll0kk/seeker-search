import type { KeyboardEvent, RefObject } from "react";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onKeyDown: (event: KeyboardEvent<HTMLInputElement>) => void;
  isLoading: boolean;
  inputRef: RefObject<HTMLInputElement | null>;
}

export function SearchBar({ value, onChange, onKeyDown, isLoading, inputRef }: SearchBarProps) {
  return (
    <div className="relative">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={onKeyDown}
        placeholder="Search for a city"
        autoComplete="off"
        autoCorrect="off"
        spellCheck={false}
        role="combobox"
        aria-expanded={value.trim().length > 0}
        aria-autocomplete="list"
        className="w-full rounded-xl border border-neutral-300 bg-white px-4 py-3 pr-11 text-base text-neutral-900 shadow-sm outline-none transition-colors placeholder:text-neutral-400 focus:border-neutral-400 focus:ring-2 focus:ring-neutral-900/5"
      />
      {isLoading && (
        <span
          aria-hidden
          className="absolute right-4 top-1/2 size-4 -translate-y-1/2 animate-spin rounded-full border-2 border-neutral-300 border-t-neutral-600"
        />
      )}
    </div>
  );
}
