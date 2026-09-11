import Foundation

/// Where the portfolio's holdings are persisted between launches.
public protocol HoldingStore {
    func load() -> [Holding]
    func save(_ holdings: [Holding])
}

/// Persists holdings as JSON in a `UserDefaults` instance.
public final class UserDefaultsHoldingStore: HoldingStore {
    public static let defaultKey = "randy_invests_holdings"

    private let defaults: UserDefaults
    private let key: String

    public init(defaults: UserDefaults = .standard, key: String = UserDefaultsHoldingStore.defaultKey) {
        self.defaults = defaults
        self.key = key
    }

    public func load() -> [Holding] {
        guard let data = defaults.data(forKey: key),
              let saved = try? JSONDecoder().decode([Holding].self, from: data) else { return [] }
        return saved
    }

    public func save(_ holdings: [Holding]) {
        guard let data = try? JSONEncoder().encode(holdings) else { return }
        defaults.set(data, forKey: key)
    }
}

/// Keeps holdings in memory only; for previews and tests.
public final class InMemoryHoldingStore: HoldingStore {
    public private(set) var holdings: [Holding]

    public init(holdings: [Holding] = []) {
        self.holdings = holdings
    }

    public func load() -> [Holding] { holdings }

    public func save(_ holdings: [Holding]) { self.holdings = holdings }
}
