import SwiftUI

struct HoldingDetailView: View {
    @EnvironmentObject var viewModel: PortfolioViewModel
    let holding: Holding

    /// Resolves the latest holding from the view model so the detail stays in
    /// sync when the position is updated (e.g. merged from Search) while open.
    private var currentHolding: Holding {
        viewModel.holdings.first(where: { $0.id == holding.id }) ?? holding
    }

    var body: some View {
        let holding = currentHolding
        return List {
            Section("Position") {
                DetailRow(label: "Shares", value: String(format: "%.4f", holding.shares))
                DetailRow(label: "Current Price", value: holding.currentPrice.formatted(.currency(code: "USD")))
                DetailRow(label: "Market Value", value: holding.marketValue.formatted(.currency(code: "USD")))
            }

            Section("Cost Basis") {
                DetailRow(label: "Avg. Cost / Share", value: holding.averageCostBasis.formatted(.currency(code: "USD")))
                DetailRow(label: "Total Cost", value: holding.totalCost.formatted(.currency(code: "USD")))
            }

            Section("Return") {
                HStack {
                    Text("Gain / Loss")
                    Spacer()
                    VStack(alignment: .trailing) {
                        Text(holding.gainLoss, format: .currency(code: "USD"))
                            .foregroundStyle(holding.gainLoss >= 0 ? .green : .red)
                        Text(holding.gainLossPercent / 100, format: .percent.precision(.fractionLength(2)))
                            .font(.caption)
                            .foregroundStyle(holding.gainLoss >= 0 ? .green : .red)
                    }
                }
            }
        }
        .navigationTitle(holding.symbol)
        .navigationBarTitleDisplayMode(.large)
    }
}

private struct DetailRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
            Spacer()
            Text(value)
                .foregroundStyle(.secondary)
        }
    }
}

#Preview {
    NavigationStack {
        HoldingDetailView(holding: Holding(
            symbol: "AAPL",
            name: "Apple Inc.",
            shares: 10,
            averageCostBasis: 150,
            currentPrice: 175
        ))
        .environmentObject(PortfolioViewModel())
    }
}
