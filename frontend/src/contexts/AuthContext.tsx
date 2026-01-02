import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, Session } from '@supabase/supabase-js';
import { supabase, auth } from '@/lib/supabase';
import { api } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signInWithOAuth: (provider: 'google') => Promise<void>;
  signOut: () => Promise<void>;
  userInfo: {
    id: string;
    email: string;
    role: string;
  } | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [userInfo, setUserInfo] = useState<{ id: string; email: string; role: string } | null>(null);

  // Initialize auth state
  useEffect(() => {
    // Get initial session
    auth.getSession().then((session) => {
      setSession(session);
      setUser(session?.user ?? null);
      if (session?.access_token) {
        localStorage.setItem('auth_token', session.access_token);
        // Fetch user info from API
        fetchUserInfo();
      }
      setLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      
      if (session?.access_token) {
        localStorage.setItem('auth_token', session.access_token);
        await fetchUserInfo();
      } else {
        localStorage.removeItem('auth_token');
        setUserInfo(null);
      }
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const fetchUserInfo = async () => {
    try {
      const info = await api.getMe();
      setUserInfo(info);
    } catch (error) {
      console.error('Failed to fetch user info:', error);
    }
  };

  const signIn = async (email: string, password: string) => {
    const data = await auth.signIn(email, password);
    if (data.session?.access_token) {
      localStorage.setItem('auth_token', data.session.access_token);
      await fetchUserInfo();
    }
  };

  const signUp = async (email: string, password: string) => {
    const data = await auth.signUp(email, password);
    if (data.session?.access_token) {
      localStorage.setItem('auth_token', data.session.access_token);
      await fetchUserInfo();
    }
  };

  const signInWithOAuth = async (provider: 'google') => {
    await auth.signInWithOAuth(provider);
  };

  const signOut = async () => {
    await auth.signOut();
    setUser(null);
    setSession(null);
    setUserInfo(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        loading,
        signIn,
        signUp,
        signInWithOAuth,
        signOut,
        userInfo,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};



