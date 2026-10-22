import { useCallback, useEffect, useMemo, useState } from "react";
import { apiRequest, getUserIdFromToken, TOKEN_KEY } from "./api.js";

const PAGE_SIZE = 10;

function AuthPanel({ onLogin, onRegister, busy, error }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function submit(event) {
    event.preventDefault();
    if (mode === "register") await onRegister(email, password);
    else await onLogin(email, password);
  }

  return (
    <section className="auth-card">
      <div className="auth-mark">g.</div>
      <p className="eyebrow">YOUR COMMUNITY, IN ONE PLACE</p>
      <h1>{mode === "login" ? "Good to see you." : "Make yourself at home."}</h1>
      <p className="muted">
        {mode === "login"
          ? "Sign in to catch up with your people."
          : "Create an account and join the conversation."}
      </p>
      <div className="auth-tabs">
        <button className={mode === "login" ? "tab active" : "tab"} onClick={() => setMode("login")} type="button">Sign in</button>
        <button className={mode === "register" ? "tab active" : "tab"} onClick={() => setMode("register")} type="button">Create account</button>
      </div>
      <form className="stack" onSubmit={submit}>
        <label>
          Email address
          <input autoComplete="email" onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" required type="email" value={email} />
        </label>
        <label>
          Password
          <input autoComplete={mode === "login" ? "current-password" : "new-password"} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" required type="password" value={password} />
        </label>
        {error && <p className="alert" role="alert">{error}</p>}
        <button className="button primary full" disabled={busy} type="submit">
          {busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create my account"}
        </button>
      </form>
      <p className="auth-footnote">A welcoming corner of the internet. Be thoughtful, be kind.</p>
    </section>
  );
}

function PostCard({ post, hasVoted, isOwner, onVote, onDelete, onUpdate, busy }) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(post.title);
  const [content, setContent] = useState(post.content);
  const [published, setPublished] = useState(post.published);
  const date = post.created_at
    ? new Date(post.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })
    : "Just now";

  async function save(event) {
    event.preventDefault();
    const saved = await onUpdate(post.id, { title, content, published });
    if (saved) setEditing(false);
  }

  return (
    <article className="post-card">
      <div className="post-heading">
        <div className="avatar">{post.owner?.email?.slice(0, 1).toUpperCase() || "G"}</div>
        <div className="post-author">
          <strong>{post.owner?.email || "Community member"}</strong>
          <span>{date}{!post.published && " · Draft"}</span>
        </div>
        {isOwner && <div className="post-menu">
          <button className="text-button" disabled={busy} onClick={() => setEditing(!editing)} type="button">{editing ? "Cancel" : "Edit"}</button>
          <button className="text-button danger-text" disabled={busy} onClick={() => onDelete(post.id)} type="button">Delete</button>
        </div>}
      </div>
      {editing ? (
        <form className="stack edit-form" onSubmit={save}>
          <label>Title<input maxLength="200" onChange={(event) => setTitle(event.target.value)} required value={title} /></label>
          <label>Your post<textarea onChange={(event) => setContent(event.target.value)} required rows="4" value={content} /></label>
          <label className="check-label"><input checked={published} onChange={(event) => setPublished(event.target.checked)} type="checkbox" /> Published</label>
          <button className="button primary" disabled={busy} type="submit">Save changes</button>
        </form>
      ) : (
        <div className="post-body"><h2>{post.title}</h2><p>{post.content}</p></div>
      )}
      <div className="post-actions">
        <button aria-pressed={hasVoted} className={hasVoted ? "vote-button voted" : "vote-button"} disabled={busy} onClick={() => onVote(post.id, hasVoted)} type="button">
          <span aria-hidden="true">{hasVoted ? "♥" : "♡"}</span>{post.votes} {post.votes === 1 ? "like" : "likes"}
        </button>
      </div>
    </article>
  );
}

function initialToken() {
  return window.localStorage.getItem(TOKEN_KEY);
}

export default function App() {
  const [token, setToken] = useState(initialToken);
  const [posts, setPosts] = useState([]);
  const [myVotes, setMyVotes] = useState(new Set());
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [published, setPublished] = useState(true);
  const [searchText, setSearchText] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [accountEmail, setAccountEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const currentUserId = useMemo(() => token ? getUserIdFromToken(token) : null, [token]);

  const loadFeed = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const query = new URLSearchParams({
        search,
        limit: String(PAGE_SIZE),
        skip: String(page * PAGE_SIZE),
      });
      const [result, votes] = await Promise.all([
        apiRequest(`/posts/?${query}`, { token }),
        apiRequest("/vote/", { token }),
      ]);
      setPosts(result.map((item) => ({ ...item.Post, votes: item.votes })));
      setMyVotes(new Set(votes));
    } catch (loadError) {
      setError(loadError.message || "Unable to load the feed.");
    } finally {
      setLoading(false);
    }
  }, [page, search, token]);

  useEffect(() => { loadFeed(); }, [loadFeed]);

  useEffect(() => {
    let active = true;
    if (!token || !currentUserId) {
      setAccountEmail("");
      return () => { active = false; };
    }
    apiRequest(`/users/${currentUserId}`, { token })
      .then((user) => {
        if (active) setAccountEmail(user.email);
      })
      .catch((requestError) => {
        if (active) setError(requestError.message || "Unable to load your account.");
      });
    return () => { active = false; };
  }, [currentUserId, token]);

  async function login(email, password) {
    setBusy(true);
    setError("");
    try {
      const result = await apiRequest("/login", {
        method: "POST",
        body: new URLSearchParams({ username: email, password }),
      });
      window.localStorage.setItem(TOKEN_KEY, result.access_token);
      setToken(result.access_token);
      setNotice("Welcome back!");
      return true;
    } catch (requestError) {
      setError(requestError.message || "Unable to sign in.");
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function register(email, password) {
    setBusy(true);
    setError("");
    try {
      await apiRequest("/users/", { method: "POST", body: JSON.stringify({ email, password }) });
      const signedIn = await login(email, password);
      if (!signedIn) setNotice("Your account was created. Sign in to continue.");
    } catch (requestError) {
      setError(requestError.message || "Unable to create your account.");
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    window.localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setPosts([]);
    setMyVotes(new Set());
    setPage(0);
    setAccountEmail("");
    setError("");
    setNotice("");
  }

  async function createPost(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await apiRequest("/posts/", { method: "POST", token, body: JSON.stringify({ title, content, published }) });
      setTitle("");
      setContent("");
      setPublished(true);
      setNotice("Your post was shared.");
      await loadFeed();
    } catch (requestError) {
      setError(requestError.message || "Unable to create your post.");
    } finally {
      setBusy(false);
    }
  }

  async function vote(postId, hasVoted) {
    setBusy(true);
    setError("");
    try {
      await apiRequest("/vote/", { method: "POST", token, body: JSON.stringify({ post_id: postId, dir: hasVoted ? 0 : 1 }) });
      await loadFeed();
    } catch (requestError) {
      setError(requestError.message || "Unable to update your vote.");
    } finally {
      setBusy(false);
    }
  }

  async function deletePost(postId) {
    if (!window.confirm("Delete this post? This cannot be undone.")) return;
    setBusy(true);
    setError("");
    try {
      await apiRequest(`/posts/${postId}`, { method: "DELETE", token });
      setNotice("Post deleted.");
      await loadFeed();
    } catch (requestError) {
      setError(requestError.message || "Unable to delete this post.");
    } finally {
      setBusy(false);
    }
  }

  async function updatePost(postId, data) {
    setBusy(true);
    setError("");
    try {
      await apiRequest(`/posts/${postId}`, { method: "PUT", token, body: JSON.stringify(data) });
      setNotice("Post updated.");
      await loadFeed();
      return true;
    } catch (requestError) {
      setError(requestError.message || "Unable to update this post.");
      return false;
    } finally {
      setBusy(false);
    }
  }

  if (!token) return (
    <main className="auth-page">
      <section className="auth-side">
        <a className="brand" href="/"><span>g.</span> gather</a>
        <div className="auth-copy">
          <p className="eyebrow">A LITTLE MORE TOGETHER</p>
          <h2>Good conversations<br />start somewhere.</h2>
          <p>Share what’s on your mind, find your people, and make space for the everyday moments.</p>
        </div>
        <span className="side-note">A welcoming corner of the internet.</span>
      </section>
      <section className="auth-main"><AuthPanel onLogin={login} onRegister={register} busy={busy} error={error} /></section>
    </main>
  );

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/"><span>g.</span> gather</a>
        <div className="topbar-right"><span className="online-label"><i /> {accountEmail || "Your space"}</span><button className="button subtle" onClick={logout} type="button">Sign out</button></div>
      </header>
      <main className="dashboard">
        <section className="welcome-row">
          <div><p className="eyebrow">YOUR COMMUNITY FEED</p><h1>A good day to connect.</h1><p className="muted">A little space to share what’s on your mind.</p></div>
          <div className="welcome-spark" aria-hidden="true">✳</div>
        </section>
        {error && <p className="alert page-alert" role="alert">{error}</p>}
        {notice && <p className="notice page-alert" role="status">{notice}</p>}
        <div className="feed-layout">
          <section className="feed-column" aria-label="Community posts">
            <form className="search-bar" onSubmit={(event) => { event.preventDefault(); setPage(0); setSearch(searchText.trim()); }}>
              <span aria-hidden="true">⌕</span>
              <input aria-label="Search posts by title" onChange={(event) => setSearchText(event.target.value)} placeholder="Find a conversation…" value={searchText} />
              {searchText && <button className="text-button" onClick={() => { setSearchText(""); setSearch(""); setPage(0); }} type="button">Clear</button>}
            </form>
            <div className="feed-title">
              <h2>{search ? "Search results" : "The latest"}</h2>
              <div className="feed-controls">
                <span>{posts.length} {posts.length === 1 ? "post" : "posts"}</span>
                <button className="text-button" disabled={loading} onClick={loadFeed} type="button">Refresh</button>
              </div>
            </div>
            {loading ? <div className="empty-card"><span className="spinner" />Loading your feed…</div> : posts.length === 0 ? (
              <div className="empty-card"><span className="empty-icon">✳</span><h3>{search ? "No posts found" : "It’s quiet in here."}</h3><p>{search ? "Try another search or clear the filter." : "Start the conversation with the first post."}</p></div>
            ) : posts.map((post) => (
              <PostCard key={post.id} busy={busy} hasVoted={myVotes.has(post.id)} isOwner={post.owner_id === currentUserId} onDelete={deletePost} onUpdate={updatePost} onVote={vote} post={post} />
            ))}
            {!loading && (page > 0 || posts.length === PAGE_SIZE) && (
              <nav className="pagination" aria-label="Feed pages">
                <button className="button subtle" disabled={loading || page === 0} onClick={() => setPage(page - 1)} type="button">Previous</button>
                <span>Page {page + 1}</span>
                <button className="button subtle" disabled={loading || posts.length < PAGE_SIZE} onClick={() => setPage(page + 1)} type="button">Next</button>
              </nav>
            )}
          </section>
          <aside className="composer-column">
            <section className="composer-card">
              <div className="composer-heading"><div className="composer-icon">✎</div><div><p className="eyebrow">YOUR VOICE MATTERS</p><h2>Share a thought</h2></div></div>
              <form className="stack" onSubmit={createPost}>
                <label>Give it a title<input maxLength="200" onChange={(event) => setTitle(event.target.value)} placeholder="What’s on your mind?" required value={title} /></label>
                <label>Write your post<textarea onChange={(event) => setContent(event.target.value)} placeholder="Share something with the community…" required rows="5" value={content} /></label>
                <label className="check-label"><input checked={published} onChange={(event) => setPublished(event.target.checked)} type="checkbox" /> Publish this post</label>
                <button className="button primary full" disabled={busy} type="submit">{busy ? "Posting…" : "Share with everyone"}</button>
              </form>
              <p className="composer-footnote">Be thoughtful. Be you. Keep it kind.</p>
            </section>
          </aside>
        </div>
      </main>
      <footer className="footer">Made for good conversations <span>✳</span></footer>
    </div>
  );
}
