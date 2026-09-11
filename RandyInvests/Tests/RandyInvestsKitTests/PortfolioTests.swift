import XCTest
@testable import RandyInvestsKit

final class PortfolioTests: XCTestCase {

    func testAddNewHolding() {
        var portfolio = Portfolio()
        portfolio.add(Holding(symbol: "MSFT", name: "Microsoft", shares: 5, averageCostBasis: 300, currentPrice: 350))
        XCTAssertEqual(portfolio.holdings.count, 1)
        XCTAssertEqual(portfolio.holdings[0].symbol, "MSFT")
    }

    func testAddDuplicateHoldingMergesAndKeepsID() {
        var portfolio = Portfolio()
        let first = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 100, currentPrice: 150)
        let second = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 200, currentPrice: 160)
        portfolio.add(first)
        portfolio.add(second)
        XCTAssertEqual(portfolio.holdings.count, 1)
        XCTAssertEqual(portfolio.holdings[0].id, first.id)
        XCTAssertEqual(portfolio.holdings[0].shares, 20, accuracy: 0.001)
        // Weighted average: (10*100 + 10*200) / 20 = 150
        XCTAssertEqual(portfolio.holdings[0].averageCostBasis, 150, accuracy: 0.001)
        XCTAssertEqual(portfolio.holdings[0].currentPrice, 160, accuracy: 0.001)
    }

    func testHoldingByIDReflectsMerge() {
        var portfolio = Portfolio()
        let first = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 100, currentPrice: 150)
        portfolio.add(first)
        portfolio.add(Holding(symbol: "AAPL", name: "Apple", shares: 5, averageCostBasis: 100, currentPrice: 150))
        XCTAssertEqual(portfolio.holding(id: first.id)?.shares ?? 0, 15, accuracy: 0.001)
    }

    func testHoldingByIDIsNilAfterRemoval() {
        let holding = Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 175)
        var portfolio = Portfolio(holdings: [holding])
        portfolio.remove(at: IndexSet(integer: 0))
        XCTAssertTrue(portfolio.holdings.isEmpty)
        XCTAssertNil(portfolio.holding(id: holding.id))
    }

    func testTotals() {
        let portfolio = Portfolio(holdings: [
            Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 200),
            Holding(symbol: "MSFT", name: "Microsoft", shares: 5, averageCostBasis: 300, currentPrice: 400)
        ])
        // 10*200 + 5*400 = 4000; cost 10*150 + 5*300 = 3000
        XCTAssertEqual(portfolio.totalMarketValue, 4000, accuracy: 0.001)
        XCTAssertEqual(portfolio.totalCost, 3000, accuracy: 0.001)
        XCTAssertEqual(portfolio.totalGainLoss, 1000, accuracy: 0.001)
        XCTAssertEqual(portfolio.totalGainLossPercent, 33.333, accuracy: 0.001)
    }

    func testTotalGainLossPercentWithNoHoldings() {
        XCTAssertEqual(Portfolio().totalGainLossPercent, 0)
    }

    func testUpdatePrice() {
        var portfolio = Portfolio(holdings: [
            Holding(symbol: "AAPL", name: "Apple", shares: 10, averageCostBasis: 150, currentPrice: 175)
        ])
        portfolio.updatePrice(for: "AAPL", newPrice: 200)
        XCTAssertEqual(portfolio.holdings[0].currentPrice, 200, accuracy: 0.001)
    }
}
