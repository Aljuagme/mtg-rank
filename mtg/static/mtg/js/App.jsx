function App() {
    const [currentView, setCurrentView] = React.useState("home");
    const [selectedDeck, setSelectedDeck] = React.useState(null);
    const [selectedPlayer, setSelectedPlayer] = React.useState(null);
    const [loggedInUser, setLoggedInUser] = React.useState([]);

    // Fetch logged-in user ID on load
    React.useEffect(() => {
        fetch(`/get_logged_in_user`)
            .then(response => response.json())
            .then(data => setLoggedInUser({
                id: data["id"],
                name: data["name"]
                })
            )
            .catch(error => console.error("Error fetching logged-in user ID:", error));
    }, []);

    console.log(`Logged in user: #${loggedInUser.name}`)

    const handleView = (view) => {
        setCurrentView(view)
        setSelectedDeck(null)
        console.log(view)

        // If "My Stats" is clicked, use logged-in user ID
        setSelectedPlayer(view === "stats" ? { id: loggedInUser.id } : null);
    }
    return (
        <div>
            {/* NavBar */}
            <RenderNavbar
                handleView={handleView}
                loggedInUser={loggedInUser}
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
                    loggedInUser={loggedInUser}
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