import Foundation

/// The holdings in a portfolio and the arithmetic over them.
public struct Portfolio: Equatable {
    public var holdings: [Holding]

    public init(holdings: [Holding] = []) {
        self.holdings = holdings
    }

    // MARK: - Totals

    public var totalMarketValue: Double {
        holdings.reduce(0) { $0 + $1.marketValue }
    }

    public var totalCost: Double {
        holdings.reduce(0) { $0 + $1.totalCost }
    }

    public var totalGainLoss: Double {
        totalMarketValue - totalCost
    }

    public var totalGainLossPercent: Double {
        guard totalCost != 0 else { return 0 }
        return (totalGainLoss / totalCost) * 100
    }

    // MARK: - Lookup

    public func holding(id: Holding.ID) -> Holding? {
        holdings.first { $0.id == id }
    }

    // MARK: - Mutations

    /// Adds a holding, merging into an existing position with the same symbol
    /// using a weighted-average cost basis.
    public mutating func add(_ holding: Holding) {
        if let index = holdings.firstIndex(where: { $0.symbol == holding.symbol }) {
            let existing = holdings[index]
            let totalShares = existing.shares + holding.shares
            let weightedCost = totalShares == 0
                ? 0
                : (existing.totalCost + holding.totalCost) / totalShares
            holdings[index] = Holding(
                id: existing.id,
                symbol: existing.symbol,
                name: existing.name,
                shares: totalShares,
                averageCostBasis: weightedCost,
                currentPrice: holding.currentPrice
            )
        } else {
            holdings.append(holding)
        }
    }

    public mutating func remove(at offsets: IndexSet) {
        for offset in offsets.sorted(by: >) where holdings.indices.contains(offset) {
            holdings.remove(at: offset)
        }
    }

    public mutating func updatePrice(for symbol: String, newPrice: Double) {
        guard let index = holdings.firstIndex(where: { $0.symbol == symbol }) else { return }
        holdings[index].currentPrice = newPrice
    }
}
