import Foundation
import Combine

final class StockPicksViewModel: ObservableObject {
    @Published var picks: [StockPick] = []

    private let saveKey = "stock_picks"

    init() {
        load()
    }

    func add(_ pick: StockPick) {
        picks.append(pick)
        save()
    }

    func delete(at offsets: IndexSet) {
        picks.remove(atOffsets: offsets)
        save()
    }

    func move(from source: IndexSet, to destination: Int) {
        picks.move(fromOffsets: source, toOffset: destination)
        save()
    }

    // MARK: - Persistence

    private func save() {
        if let data = try? JSONEncoder().encode(picks) {
            UserDefaults.standard.set(data, forKey: saveKey)
        }
    }

    private func load() {
        guard let data = UserDefaults.standard.data(forKey: saveKey),
              let saved = try? JSONDecoder().decode([StockPick].self, from: data) else {
            picks = Self.samplePicks
            return
        }
        picks = saved
    }

    // MARK: - Sample data

    static let samplePicks: [StockPick] = [
        StockPick(ticker: "AAPL", companyName: "Apple Inc.", targetPrice: 230.00,
                  notes: "Strong ecosystem, services growth continuing."),
        StockPick(ticker: "NVDA", companyName: "NVIDIA Corporation", targetPrice: 1400.00,
                  notes: "AI infrastructure demand remains robust."),
        StockPick(ticker: "MSFT", companyName: "Microsoft Corporation", targetPrice: 480.00,
                  notes: "Azure + Copilot monetization on track."),
    ]
}
