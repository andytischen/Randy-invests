import Foundation

/// Represents a single holding in the portfolio.
struct Holding: Identifiable, Codable, Equatable {
    var id: UUID
    var symbol: String
    var name: String
    var shares: Double
    var averageCostBasis: Double
    var currentPrice: Double

    init(
        id: UUID = UUID(),
        symbol: String,
        name: String,
        shares: Double,
        averageCostBasis: Double,
        currentPrice: Double
    ) {
        self.id = id
        self.symbol = symbol
        self.name = name
        self.shares = shares
        self.averageCostBasis = averageCostBasis
        self.currentPrice = currentPrice
    }

    /// Total market value of this holding.
    var marketValue: Double {
        shares * currentPrice
    }

    /// Total cost basis of this holding.
    var totalCost: Double {
        shares * averageCostBasis
    }

    /// Unrealised gain/loss in dollars.
    var gainLoss: Double {
        marketValue - totalCost
    }

    /// Unrealised gain/loss as a percentage.
    var gainLossPercent: Double {
        guard totalCost != 0 else { return 0 }
        return (gainLoss / totalCost) * 100
    }
}
