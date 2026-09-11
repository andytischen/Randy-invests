import SwiftUI
import RandyInvestsKit

struct HoldingRowView: View {
    let holding: Holding

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text(holding.symbol)
                    .font(.headline)
                Text(holding.name)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }

            Spacer()

            VStack(alignment: .trailing, spacing: 2) {
                Text(holding.marketValue, format: .currency(code: "USD"))
                    .font(.subheadline.bold())
                HStack(spacing: 2) {
                    Image(systemName: holding.gainLoss >= 0 ? "arrow.up" : "arrow.down")
                        .imageScale(.small)
                    Text(holding.gainLossPercent / 100, format: .percent.precision(.fractionLength(2)))
                }
                .font(.caption)
                .foregroundStyle(holding.gainLoss >= 0 ? .green : .red)
            }
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    HoldingRowView(holding: Holding(
        symbol: "AAPL",
        name: "Apple Inc.",
        shares: 10,
        averageCostBasis: 150,
        currentPrice: 175
    ))
}
