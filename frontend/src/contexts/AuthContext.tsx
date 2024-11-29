import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { auth } from '../firebase'
import { signInWithEmailAndPassword, signOut } from 'firebase/auth'
import { useNavigate } from 'react-router-dom'

import { User } from '../types/user'

interface AuthContextType {
  currentUser: any
  logout: () => Promise<void>
  login: (email: string, password: string) => Promise<any>
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
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const updateTokenAndSetUser = async (user: any) => {
    const token = await user.getIdToken();
    const loggedUser: User = {
      id: user.uid,
      email: user.email,
      token: token
    }
    setCurrentUser(loggedUser)
  }

  const updateUserSession = async (user: any) => {
    if (user) {
      try {
        await updateTokenAndSetUser(user)
      } catch (error) {
        console.error("Token refresh failed:", error)
        await logout()
        navigate('/login')
      }
    } else {
      setCurrentUser(null)
    }
  }

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (user: any) => {
      await updateUserSession(user)
      setLoading(false)
    })

    const refreshTokenInterval = setInterval(async () => {
      await updateUserSession(auth.currentUser)
    }, 10 * 60 * 1000)

    return () => {
      unsubscribe()
      clearInterval(refreshTokenInterval)
    }
  }, [navigate])

  const login = async (email: string, password: string) => {
    return await signInWithEmailAndPassword(auth, email, password)
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