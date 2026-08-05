import SwiftUI

struct ContentView: View {
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Image(systemName: "chart.line.uptrend.xyaxis")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 80, height: 80)
                    .foregroundColor(.accentColor)

                Text("Randy Invests")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Text("Your personal investment tracker")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            .padding()
            .navigationTitle("Randy Invests")
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
