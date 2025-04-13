import './styles/variables.css';
import { Route, Routes } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import PrivateRoute from "./routes/PrivateRoute";
import Login from "./components/auth/Login";
import { ToastContainer, Slide } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import NotFound from "./components/common/NotFound/NotFound";
import Chat from './pages/chat/Chat';
import About from './pages/about/About';

function App() {
  return (
    <div>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<PrivateRoute component={Chat} />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
        <ToastContainer
          position="bottom-center"
          autoClose={2500}
          hideProgressBar={false}
          closeOnClick={false}
          pauseOnHover={true}
          draggable={true}
          theme="dark"
          transition={Slide}
        />
      </AuthProvider>
    </div>
  );
}

export default App;
