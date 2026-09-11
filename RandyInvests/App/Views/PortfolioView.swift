import SwiftUI
import RandyInvestsKit

struct PortfolioView: View {
    @EnvironmentObject var viewModel: PortfolioViewModel
    @State private var showingAddSheet = false

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.holdings.isEmpty {
                    emptyState
                } else {
                    holdingsList
                }
            }
            .navigationTitle("My Portfolio")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button {
                        showingAddSheet = true
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showingAddSheet) {
                AddHoldingView()
            }
        }
    }

    // MARK: - Subviews

    private var emptyState: some View {
        ContentUnavailableView(
            "No Holdings Yet",
            systemImage: "chart.pie",
            description: Text("Tap + to add your first investment.")
        )
    }

    private var holdingsList: some View {
        List {
            summarySection
            holdingsSection
        }
    }

    private var summarySection: some View {
        Section {
            VStack(spacing: 12) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Total Value")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        Text(viewModel.totalMarketValue, format: .currency(code: "USD"))
                            .font(.title2.bold())
                    }
                    Spacer()
                    VStack(alignment: .trailing, spacing: 4) {
                        Text("Total Return")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        HStack(spacing: 4) {
                            Image(systemName: viewModel.totalGainLoss >= 0 ? "arrow.up" : "arrow.down")
                            Text(viewModel.totalGainLoss, format: .currency(code: "USD"))
                        }
                        .font(.subheadline.bold())
                        .foregroundStyle(viewModel.totalGainLoss >= 0 ? .green : .red)
                        Text(viewModel.totalGainLossPercent / 100, format: .percent.precision(.fractionLength(2)))
                            .font(.caption)
                            .foregroundStyle(viewModel.totalGainLoss >= 0 ? .green : .red)
                    }
                }
            }
            .padding(.vertical, 8)
        } header: {
            Text("Summary")
        }
    }

    private var holdingsSection: some View {
        Section {
            ForEach(viewModel.holdings) { holding in
                NavigationLink(destination: HoldingDetailView(holdingID: holding.id)) {
                    HoldingRowView(holding: holding)
                }
            }
            .onDelete { offsets in
                viewModel.removeHoldings(at: offsets)
            }
        } header: {
            Text("Holdings")
        }
    }
}

#Preview {
    PortfolioView()
        .environmentObject(PortfolioViewModel.preview())
}
