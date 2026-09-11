import XCTest
@testable import RandyInvestsKit

final class DecimalInputTests: XCTestCase {
    private let us = Locale(identifier: "en_US")
    private let de = Locale(identifier: "de_DE")

    func testPeriodDecimalInPeriodLocale() {
        XCTAssertEqual(DecimalInput.parse("12.5", locale: us) ?? 0, 12.5, accuracy: 0.0001)
        XCTAssertEqual(DecimalInput.parse("0.25", locale: us) ?? 0, 0.25, accuracy: 0.0001)
    }

    func testCommaDecimalInCommaLocale() {
        XCTAssertEqual(DecimalInput.parse("12,5", locale: de) ?? 0, 12.5, accuracy: 0.0001)
        XCTAssertEqual(DecimalInput.parse("0,25", locale: de) ?? 0, 0.25, accuracy: 0.0001)
    }

    func testPeriodDecimalStillAcceptedInCommaLocale() {
        XCTAssertEqual(DecimalInput.parse("12.5", locale: de) ?? 0, 12.5, accuracy: 0.0001)
    }

    func testIntegersParseInBothLocales() {
        XCTAssertEqual(DecimalInput.parse("100", locale: us), 100)
        XCTAssertEqual(DecimalInput.parse("100", locale: de), 100)
    }

    func testWhitespaceIsTrimmed() {
        XCTAssertEqual(DecimalInput.parse(" 7.5 ", locale: us) ?? 0, 7.5, accuracy: 0.0001)
    }

    func testGarbageIsRejected() {
        XCTAssertNil(DecimalInput.parse("", locale: us))
        XCTAssertNil(DecimalInput.parse("abc", locale: us))
        XCTAssertNil(DecimalInput.parse("1.2.3", locale: us))
    }

    func testParsePositiveRejectsZeroAndNegatives() {
        XCTAssertNil(DecimalInput.parsePositive("0", locale: us))
        XCTAssertNil(DecimalInput.parsePositive("-3", locale: us))
        XCTAssertNil(DecimalInput.parsePositive("-3,5", locale: de))
        XCTAssertEqual(DecimalInput.parsePositive("3,5", locale: de) ?? 0, 3.5, accuracy: 0.0001)
    }
}
