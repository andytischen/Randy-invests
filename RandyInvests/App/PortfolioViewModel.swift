import Foundation
import Combine
import RandyInvestsKit

@MainActor
final class PortfolioViewModel: ObservableObject {
    @Published private(set) var portfolio: Portfolio
    @Published var isLoading: Bool = false

    private let store: HoldingStore

    init(store: HoldingStore = UserDefaultsHoldingStore()) {
        self.store = store
        self.portfolio = Portfolio(holdings: store.load())
    }

    var holdings: [Holding] { portfolio.holdings }
    var totalMarketValue: Double { portfolio.totalMarketValue }
    var totalCost: Double { portfolio.totalCost }
    var totalGainLoss: Double { portfolio.totalGainLoss }
    var totalGainLossPercent: Double { portfolio.totalGainLossPercent }

    func holding(id: Holding.ID) -> Holding? {
        portfolio.holding(id: id)
    }

    // MARK: - Mutations

    func addHolding(_ holding: Holding) {
        portfolio.add(holding)
        store.save(portfolio.holdings)
    }

    func removeHoldings(at offsets: IndexSet) {
        portfolio.remove(at: offsets)
        store.save(portfolio.holdings)
    }

    func updatePrice(for symbol: String, newPrice: Double) {
        portfolio.updatePrice(for: symbol, newPrice: newPrice)
        store.save(portfolio.holdings)
    }
}

extension PortfolioViewModel {
    /// A view model backed by memory only, for previews.
    static func preview(holdings: [Holding] = []) -> PortfolioViewModel {
        PortfolioViewModel(store: InMemoryHoldingStore(holdings: holdings))
    }
}
