import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { auth } from '../firebase'
import { signInWithEmailAndPassword, signOut, User as FirebaseUser } from 'firebase/auth'

interface AuthContextType {
  currentUser: FirebaseUser | null;
  getIdToken: () => Promise<string>;
  login: (email: string, password: string) => Promise<any>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined | any>(undefined)
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<FirebaseUser | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (user: any) => {
      setCurrentUser(user)
      setLoading(false)
    })

    return unsubscribe;
  }, [auth]);

  const getIdToken = async () => {
    if (!currentUser) {
      throw new Error('No user is signed in');
    }
    return await currentUser.getIdToken(true);
  };

  const login = async (email: string, password: string) => {
    return await signInWithEmailAndPassword(auth, email, password);
  };

  const logout = () => {
    return signOut(auth);
  }

  const value = {
    currentUser,
    getIdToken,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  )
}