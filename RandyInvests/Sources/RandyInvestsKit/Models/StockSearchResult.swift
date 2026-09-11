import Foundation

/// Represents a stock search result.
public struct StockSearchResult: Identifiable, Equatable {
    public var id: String { symbol }
    public let symbol: String
    public let name: String
    public let exchange: String

    public init(symbol: String, name: String, exchange: String) {
        self.symbol = symbol
        self.name = name
        self.exchange = exchange
    }
}
