import Foundation

struct StockPick: Identifiable, Codable {
    var id: UUID = UUID()
    var ticker: String
    var companyName: String
    var targetPrice: Double
    var notes: String
    var dateAdded: Date = Date()

    var formattedTargetPrice: String {
        String(format: "$%.2f", targetPrice)
    }
}
