
import React, { createContext, useState, useEffect, useContext } from 'react';
import { mockData } from '../data/mockData'; // Import the mock data

// Create the context
const DataContext = createContext();

// Create a provider component
export const DataProvider = ({ children }) => {
  const [repositories, setRepositories] = useState([]);
  const [contributors, setContributors] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function to fetch data with localStorage cache support
  const fetchData = async () => {
    setIsLoading(true);
    setError(null);

    // Try loading from localStorage cache first for fast initial load
    const cachedRepos = localStorage.getItem('cached_repositories');
    const cachedContribs = localStorage.getItem('cached_contributors');
    if (cachedRepos && cachedContribs) {
      try {
        setRepositories(JSON.parse(cachedRepos));
        setContributors(JSON.parse(cachedContribs));
      } catch (err) {
        console.warn('Failed parsing cached telemetry:', err);
      }
    }

    try {
      const backendUrl = 'http://localhost:8000/api/get_data/';
      const response = await fetch(backendUrl);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const repos = data.repositories || [];
      const contribs = data.contributors || [];
      setRepositories(repos);
      setContributors(contribs);

      // Persist telemetry to local cache
      localStorage.setItem('cached_repositories', JSON.stringify(repos));
      localStorage.setItem('cached_contributors', JSON.stringify(contribs));
    } catch (e) {
      console.error("Failed to fetch from backend, using fallback data:", e);
      if (!cachedRepos || !cachedContribs) {
        setRepositories(mockData.repositories || []);
        setContributors(mockData.contributors || []);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch data on component mount
  useEffect(() => {
    fetchData();
  }, []); // Empty dependency array ensures this runs only once on mount

  // Value provided by the context
  const value = {
    repositories,
    contributors,
    isLoading,
    error,
    refreshData: fetchData // Expose a function to refetch if needed
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};

// Custom hook to easily consume the context
export const useData = () => {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};