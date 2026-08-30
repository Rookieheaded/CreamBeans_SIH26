import {Navigate,useLocation} from 'react-router-dom'
import {useAuth} from '../context/AuthContext'
export default function RequireAuth({children}){const {isAuthenticated}=useAuth();const loc=useLocation();return isAuthenticated?children:<Navigate to="/login" replace state={{from:loc.pathname}}/>}
