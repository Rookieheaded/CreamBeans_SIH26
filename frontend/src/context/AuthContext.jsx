import {createContext,useContext,useMemo,useState} from 'react'
import {api,getToken} from '../api/client'

const AuthContext=createContext(null)
export function AuthProvider({children}){
  const [user,setUser]=useState(()=>{
    try{return JSON.parse(localStorage.getItem('current_user')||'null')}catch{return null}
  })
  const [loading,setLoading]=useState(false)
  const login=async(email,password)=>{
    setLoading(true)
    try{
      const data=await api.login(email,password)
      localStorage.setItem('access_token',data.access_token)
      const next={id:data.user_id,email:data.email||email}
      localStorage.setItem('current_user',JSON.stringify(next)); setUser(next); return data
    } finally {setLoading(false)}
  }
  const logout=()=>{localStorage.removeItem('access_token');localStorage.removeItem('current_user');setUser(null)}
  const handle401=()=>logout()
  const value=useMemo(()=>({user,isAuthenticated:!!getToken(),loading,login,logout,handle401}),[user,loading])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
export const useAuth=()=>useContext(AuthContext)
