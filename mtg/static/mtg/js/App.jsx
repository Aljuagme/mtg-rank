function App() {
    const [currentView, setCurrentView] = React.useState("home");
    const [selectedDeck, setSelectedDeck] = React.useState(null);
    const [selectedPlayer, setSelectedPlayer] = React.useState(null);
    const [loggedInUserId, setLoggedInUserId] = React.useState(null);

    // Fetch logged-in user ID on load
    React.useEffect(() => {
        fetch(`/get_logged_in_user`)
            .then(response => response.json())
            .then(data => setLoggedInUserId(data.id)
            )
            .catch(error => console.error("Error fetching logged-in user ID:", error));
    }, []);

    console.log(`Logged in user: #${loggedInUserId}`)

    const handleView = (view) => {
        setCurrentView(view)
        setSelectedDeck(null)
        console.log(view)

        // If "My Stats" is clicked, use logged-in user ID
        setSelectedPlayer(view === "stats" ? { id: loggedInUserId } : null);
    }
    return (
        <div>
            {/* NavBar */}
            <RenderNavbar
                handleView={handleView}
                loggedInUserId={loggedInUserId}
            />
            <hr />

            {/* View */}
            {selectedDeck ? (
                <RenderDeck
                    selectedDeck={selectedDeck}
                    setSelectedDeck={setSelectedDeck}
                    setSelectedPlayer={setSelectedPlayer}
                />
            ) : selectedPlayer ?  (
                <RenderPlayer
                    selectedPlayer={selectedPlayer}
                    setSelectedDeck={setSelectedDeck}
                    loggedInUserId={loggedInUserId}
                />
            ) : currentView === "decks" ? (
                <RenderBestDecks
                    setSelectedPlayer={setSelectedPlayer}
                    setSelectedDeck={setSelectedDeck}
                />
            ) : (
                <RenderResults
                    setSelectedDeck={setSelectedDeck}
                    setSelectedPlayer={setSelectedPlayer}
                />
            )}
        </div>
    );
}