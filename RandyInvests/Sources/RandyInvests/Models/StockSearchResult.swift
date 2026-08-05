import Foundation

/// Represents a stock search result.
struct StockSearchResult: Identifiable, Equatable {
    var id: String { symbol }
    let symbol: String
    let name: String
    let exchange: String
}
