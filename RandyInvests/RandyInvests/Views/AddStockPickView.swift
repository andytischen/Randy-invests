import SwiftUI

struct AddStockPickView: View {
    @Environment(\.dismiss) private var dismiss
    @ObservedObject var viewModel: StockPicksViewModel

    @State private var ticker: String = ""
    @State private var companyName: String = ""
    @State private var targetPrice: String = ""
    @State private var notes: String = ""
    @State private var showValidationError = false

    var body: some View {
        NavigationView {
            Form {
                Section("Stock") {
                    TextField("Ticker (e.g. AAPL)", text: $ticker)
                        .textInputAutocapitalization(.characters)
                        .autocorrectionDisabled()
                    TextField("Company Name", text: $companyName)
                }

                Section("Target Price") {
                    TextField("$0.00", text: $targetPrice)
                        .keyboardType(.decimalPad)
                }

                Section("Notes") {
                    TextEditor(text: $notes)
                        .frame(minHeight: 80)
                }

                if showValidationError {
                    Section {
                        Text("Please fill in ticker, company name, and a valid target price.")
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                }
            }
            .navigationTitle("Add Stock Pick")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Add") { submit() }
                        .fontWeight(.semibold)
                }
            }
        }
    }

    private func submit() {
        let trimmedTicker = ticker.trimmingCharacters(in: .whitespaces).uppercased()
        let trimmedName = companyName.trimmingCharacters(in: .whitespaces)
        guard !trimmedTicker.isEmpty,
              !trimmedName.isEmpty,
              let price = Double(targetPrice), price > 0 else {
            showValidationError = true
            return
        }
        let pick = StockPick(
            ticker: trimmedTicker,
            companyName: trimmedName,
            targetPrice: price,
            notes: notes.trimmingCharacters(in: .whitespacesAndNewlines)
        )
        viewModel.add(pick)
        dismiss()
    }
}
