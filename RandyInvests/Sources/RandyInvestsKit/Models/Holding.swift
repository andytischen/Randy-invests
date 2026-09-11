import Foundation

/// Represents a single holding in the portfolio.
public struct Holding: Identifiable, Codable, Equatable {
    public var id: UUID
    public var symbol: String
    public var name: String
    public var shares: Double
    public var averageCostBasis: Double
    public var currentPrice: Double

    public init(
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
    public var marketValue: Double {
        shares * currentPrice
    }

    /// Total cost basis of this holding.
    public var totalCost: Double {
        shares * averageCostBasis
    }

    /// Unrealised gain/loss in dollars.
    public var gainLoss: Double {
        marketValue - totalCost
    }

    /// Unrealised gain/loss as a percentage.
    public var gainLossPercent: Double {
        guard totalCost != 0 else { return 0 }
        return (gainLoss / totalCost) * 100
    }
}
