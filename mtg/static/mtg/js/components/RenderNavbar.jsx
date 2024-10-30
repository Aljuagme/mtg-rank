const RenderNavbar = ({handleView}) => {
    return (
        <div className="navbar">
                <button className="btn btn-sm btn-outline-primary" onClick={() => handleView("home")}>Home</button>
                <button className="btn btn-sm btn-outline-primary" onClick={() => handleView("stats")}>My Stats</button>
                <button className="btn btn-sm btn-outline-primary" onClick={() => handleView("decks")}>Best Decks</button>
                <button className="btn btn-sm btn-outline-primary" onClick={() => handleView("chart")}>Chart</button>
                <button className="btn btn-sm btn-outline-primary" onClick={() => handleView("tournament")}>Tournament</button>
                <a className="btn btn-danger out" href="/logout">Log Out</a>
            <hr/>
        </div>
    );
};
