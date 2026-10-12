// TC-015: React Maintainability (MAINT13, MAINT14)
// Demonstrates massive multi-responsibility component with deep prop drilling vs. custom hook decomposition

import React, { useState, useEffect } from "react";

interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
}

// --- VIOLATION ---
// VIOLATION: Giant component combining API data fetching, form state, complex validation,
// and presentation all tangled together without custom hooks or decomposition (MAINT14).
export const UserManagementDashboardViolation: React.FC = () => {
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch("/api/users")
      .then((res) => res.json())
      .then((data) => {
        setUsers(data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Failed to fetch");
        setLoading(false);
      });
  }, []);

  const filteredUsers = users.filter((u) =>
    u.name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div>
      <input
        type="text"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter users..."
      />
      {loading && <p>Loading users...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <ul>
        {filteredUsers.map((user) => (
          <li key={user.id}>
            {user.name} ({user.email}) - {user.role}
          </li>
        ))}
      </ul>
    </div>
  );
};

// --- SAFE IMPLEMENTATION ---
function useUserDirectory() {
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch("/api/users")
      .then((res) => res.json())
      .then((data) => {
        setUsers(data);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load");
        setLoading(false);
      });
  }, []);

  return { users, loading, error };
}

export const UserManagementDashboardSafe: React.FC = () => {
  const { users, loading, error } = useUserDirectory();
  const [filter, setFilter] = useState("");

  const filtered = users.filter((u) =>
    u.name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div>
      <input
        type="text"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter users..."
      />
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      <ul>
        {filtered.map((user) => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  );
};

