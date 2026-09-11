import Foundation

extension String {
    /// Parses the string into a `Double` using the current locale's decimal
    /// separator (e.g. "," in many European locales), falling back to the
    /// POSIX/period separator. Returns `nil` if the value cannot be parsed.
    func parsedDouble(locale: Locale = .current) -> Double? {
        let trimmed = trimmingCharacters(in: .whitespaces)
        guard !trimmed.isEmpty else { return nil }

        let formatter = NumberFormatter()
        formatter.locale = locale
        formatter.numberStyle = .decimal
        if let number = formatter.number(from: trimmed) {
            return number.doubleValue
        }

        // Fall back to period-decimal parsing for input that uses "."
        return Double(trimmed)
    }
}
