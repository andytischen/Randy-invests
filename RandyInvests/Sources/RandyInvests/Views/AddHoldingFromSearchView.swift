import SwiftUI

/// Sheet presented when adding a holding from a search result.
struct AddHoldingFromSearchView: View {
    @EnvironmentObject var viewModel: PortfolioViewModel
    @Environment(\.dismiss) private var dismiss

    let searchResult: StockSearchResult

    @State private var sharesText = ""
    @State private var costBasisText = ""
    @State private var currentPriceText = ""
    @State private var showValidationError = false
    @State private var validationMessage = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("Stock") {
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(searchResult.symbol).font(.headline)
                            Text(searchResult.name).font(.caption).foregroundStyle(.secondary)
                        }
                        Spacer()
                        Text(searchResult.exchange)
                            .font(.caption2)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 3)
                            .background(.quaternary)
                            .clipShape(RoundedRectangle(cornerRadius: 4))
                    }
                }

                Section("Trade Details") {
                    TextField("Number of Shares", text: $sharesText)
                        .keyboardType(.decimalPad)

                    TextField("Average Cost / Share ($)", text: $costBasisText)
                        .keyboardType(.decimalPad)

                    TextField("Current Price ($)", text: $currentPriceText)
                        .keyboardType(.decimalPad)
                }
            }
            .navigationTitle("Add \(searchResult.symbol)")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Add") { addHolding() }
                        .disabled(!isFormValid)
                }
            }
            .alert("Invalid Input", isPresented: $showValidationError) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(validationMessage)
            }
        }
    }

    private var isFormValid: Bool {
        Double(sharesText) != nil &&
        Double(costBasisText) != nil &&
        Double(currentPriceText) != nil
    }

    private func addHolding() {
        guard let shares = Double(sharesText), shares > 0 else {
            validationMessage = "Shares must be a positive number."
            showValidationError = true
            return
        }
        guard let costBasis = Double(costBasisText), costBasis > 0 else {
            validationMessage = "Cost basis must be a positive number."
            showValidationError = true
            return
        }
        guard let currentPrice = Double(currentPriceText), currentPrice > 0 else {
            validationMessage = "Current price must be a positive number."
            showValidationError = true
            return
        }

        let holding = Holding(
            symbol: searchResult.symbol,
            name: searchResult.name,
            shares: shares,
            averageCostBasis: costBasis,
            currentPrice: currentPrice
        )
        viewModel.addHolding(holding)
        dismiss()
    }
}

#Preview {
    AddHoldingFromSearchView(
        searchResult: StockSearchResult(symbol: "AAPL", name: "Apple Inc.", exchange: "NASDAQ")
    )
    .environmentObject(PortfolioViewModel())
}
