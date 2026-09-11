import XCTest
@testable import RandyInvestsKit

final class HoldingTests: XCTestCase {

    func testMarketValue() {
        let holding = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 200)
        XCTAssertEqual(holding.marketValue, 2000, accuracy: 0.001)
    }

    func testTotalCost() {
        let holding = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 200)
        XCTAssertEqual(holding.totalCost, 1500, accuracy: 0.001)
    }

    func testGainLoss() {
        let holding = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 200)
        XCTAssertEqual(holding.gainLoss, 500, accuracy: 0.001)
    }

    func testGainLossPercent() {
        let holding = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 200)
        XCTAssertEqual(holding.gainLossPercent, 33.333, accuracy: 0.001)
    }

    func testGainLossPercentWithZeroCost() {
        let holding = Holding(symbol: "FREE", name: "Free Stock", shares: 10, averageCostBasis: 0, currentPrice: 100)
        XCTAssertEqual(holding.gainLossPercent, 0)
    }
}
