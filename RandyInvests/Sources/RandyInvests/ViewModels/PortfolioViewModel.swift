import Foundation
import Combine

@MainActor
final class PortfolioViewModel: ObservableObject {
    @Published var holdings: [Holding] = []
    @Published var isLoading: Bool = false

    private let storageKey = "randy_invests_holdings"

    init() {
        loadHoldings()
    }

    // MARK: - Computed properties

    var totalMarketValue: Double {
        holdings.reduce(0) { $0 + $1.marketValue }
    }

    var totalCost: Double {
        holdings.reduce(0) { $0 + $1.totalCost }
    }

    var totalGainLoss: Double {
        totalMarketValue - totalCost
    }

    var totalGainLossPercent: Double {
        guard totalCost != 0 else { return 0 }
        return (totalGainLoss / totalCost) * 100
    }

    // MARK: - Mutations

    func addHolding(_ holding: Holding) {
        if let index = holdings.firstIndex(where: { $0.symbol == holding.symbol }) {
            // Merge with existing holding using weighted average cost
            let existing = holdings[index]
            let totalShares = existing.shares + holding.shares
            let weightedCost = (existing.totalCost + holding.totalCost) / totalShares
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
        saveHoldings()
    }

    func removeHoldings(at offsets: IndexSet) {
        holdings.remove(atOffsets: offsets)
        saveHoldings()
    }

    func updatePrice(for symbol: String, newPrice: Double) {
        guard let index = holdings.firstIndex(where: { $0.symbol == symbol }) else { return }
        holdings[index].currentPrice = newPrice
        saveHoldings()
    }

    // MARK: - Persistence

    private func saveHoldings() {
        if let data = try? JSONEncoder().encode(holdings) {
            UserDefaults.standard.set(data, forKey: storageKey)
        }
    }

    private func loadHoldings() {
        guard let data = UserDefaults.standard.data(forKey: storageKey),
              let saved = try? JSONDecoder().decode([Holding].self, from: data) else { return }
        holdings = saved
    }
}
