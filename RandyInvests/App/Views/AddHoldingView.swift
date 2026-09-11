import SwiftUI
import RandyInvestsKit

struct AddHoldingView: View {
    @EnvironmentObject var viewModel: PortfolioViewModel
    @Environment(\.dismiss) private var dismiss

    @State private var symbol = ""
    @State private var name = ""
    @State private var sharesText = ""
    @State private var costBasisText = ""
    @State private var currentPriceText = ""
    @State private var showValidationError = false
    @State private var validationMessage = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("Stock Details") {
                    TextField("Symbol (e.g. AAPL)", text: $symbol)
                        .textInputAutocapitalization(.characters)
                        .autocorrectionDisabled()

                    TextField("Company Name", text: $name)
                        .autocorrectionDisabled()
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
            .navigationTitle("Add Holding")
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

    // MARK: - Validation

    private var isFormValid: Bool {
        !symbol.trimmingCharacters(in: .whitespaces).isEmpty &&
        !name.trimmingCharacters(in: .whitespaces).isEmpty &&
        DecimalInput.parsePositive(sharesText) != nil &&
        DecimalInput.parsePositive(costBasisText) != nil &&
        DecimalInput.parsePositive(currentPriceText) != nil
    }

    // MARK: - Actions

    private func addHolding() {
        guard let shares = DecimalInput.parsePositive(sharesText) else {
            validationMessage = "Shares must be a positive number."
            showValidationError = true
            return
        }
        guard let costBasis = DecimalInput.parsePositive(costBasisText) else {
            validationMessage = "Cost basis must be a positive number."
            showValidationError = true
            return
        }
        guard let currentPrice = DecimalInput.parsePositive(currentPriceText) else {
            validationMessage = "Current price must be a positive number."
            showValidationError = true
            return
        }

        let holding = Holding(
            symbol: symbol.trimmingCharacters(in: .whitespaces).uppercased(),
            name: name.trimmingCharacters(in: .whitespaces),
            shares: shares,
            averageCostBasis: costBasis,
            currentPrice: currentPrice
        )
        viewModel.addHolding(holding)
        dismiss()
    }
}

#Preview {
    AddHoldingView()
        .environmentObject(PortfolioViewModel.preview())
}
