const RenderNavbar = ({handleView, loggedInUser}) => {
    return (
        <div className="navbar">
            <button className="btn btn-sm btn-outline-primary" onClick={() => handleView("home")}>Home</button>
            <button className="btn btn-sm btn-outline-primary" onClick={() => handleView("stats")}>My Stats</button>
            <button className="btn btn-sm btn-outline-primary" onClick={() => handleView("decks")}>Best Decks</button>
            <button className="btn btn-sm btn-outline-primary" onClick={() => handleView("chart")}>Chart</button>
            <a className="btn btn-sm btn-outline-primary tournament" href="http://localhost:8000/tournament">Tournament</a>
            <span className="user-name">{loggedInUser.name}</span>
            <a className="btn btn-danger out" href="/logout">Log Out</a>
        </div>
    );
};
