// TC-012: Component and UI Modularity

import React, { useState, useEffect } from 'react';

// VIOLATION: UI component mixing API fetching, state orchestration, complex formatting, and JSX markup
export const UserProfileWidgetViolation: React.FC<{ userId: string }> = ({ userId }) => {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(data => {
        setUser(data);
        setLoading(false);
      });
  }, [userId]);

  if (loading) return <div>Loading user...</div>;

  return (
    <div className="profile-card">
      <h2>{user.name}</h2>
      <p>Email: {user.email}</p>
      <p>Member Since: {new Date(user.createdAt).toLocaleDateString()}</p>
    </div>
  );
};


// SAFE: Container logic extracted into custom hook, presentational UI kept focused
function useUserProfile(userId: string) {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(data => {
        setUser(data);
        setLoading(false);
      });
  }, [userId]);

  return { user, loading };
}

export const UserProfileWidgetSafe: React.FC<{ userId: string }> = ({ userId }) => {
  const { user, loading } = useUserProfile(userId);

  if (loading) return <div>Loading user...</div>;

  return (
    <div className="profile-card">
      <h2>{user.name}</h2>
      <p>Email: {user.email}</p>
      <p>Member Since: {new Date(user.createdAt).toLocaleDateString()}</p>
    </div>
  );
};

