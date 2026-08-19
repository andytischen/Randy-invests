import XCTest

final class RandyInvestsUITests: XCTestCase {

    var app: XCUIApplication!

    override func setUpWithError() throws {
        try super.setUpWithError()
        continueAfterFailure = false
        app = XCUIApplication()
    }

    func testLaunch() throws {
        // Verify the app launches successfully
        app.launch()
        XCTAssertTrue(app.staticTexts["Randy Invests"].exists)
    }

    func testLaunchPerformance() throws {
        measure(metrics: [XCTApplicationLaunchMetric()]) {
            XCUIApplication().launch()
        }
    }
}
