import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { auth } from '../firebase'
import { signInWithEmailAndPassword, signOut } from 'firebase/auth'

import { User } from '../types/user'

const AuthContext = createContext<AuthContextType | undefined | any>(undefined)
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (user: any) => {
      if (user) {
        const loggedUser: User = {
          id: user.uid,
          email: user.email,
        }
        setCurrentUser(loggedUser)
      } else {
        setCurrentUser(null)
      }
      setLoading(false)
    })

    return unsubscribe
  }, [])

  const login = async (email: string, password: string) => {
    return await signInWithEmailAndPassword(auth, email, password);
  }

  const logout = () => {
    return signOut(auth)
  }

  const value = {
    currentUser,
    logout,
    login
  }

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  )
}

interface AuthContextType {
  currentUser: any
  logout: () => Promise<void>
  login: (email: string, password: string) => Promise<any>
}