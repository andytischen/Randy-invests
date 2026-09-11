import Foundation

/// Parses numbers typed into a text field, honouring the locale's decimal
/// separator (the one the decimal keypad shows) and also accepting a plain
/// period so pasted or programmatic values still work everywhere.
public enum DecimalInput {
    public static func parse(_ text: String, locale: Locale = .current) -> Double? {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }

        let separators = Set([locale.decimalSeparator ?? ".", "."].flatMap { $0 })
        var normalized = ""
        var sawSeparator = false
        for (offset, character) in trimmed.enumerated() {
            if separators.contains(character) {
                guard !sawSeparator else { return nil }
                sawSeparator = true
                normalized.append(".")
            } else if character.isASCII && character.isNumber {
                normalized.append(character)
            } else if character == "-" && offset == 0 {
                normalized.append(character)
            } else {
                return nil
            }
        }

        return Double(normalized)
    }

    /// Parses like `parse(_:locale:)` and additionally requires the value to
    /// be strictly positive.
    public static func parsePositive(_ text: String, locale: Locale = .current) -> Double? {
        guard let value = parse(text, locale: locale), value > 0, value.isFinite else { return nil }
        return value
    }
}
