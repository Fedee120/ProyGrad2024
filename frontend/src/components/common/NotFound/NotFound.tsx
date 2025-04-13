import { useNavigate } from "react-router-dom"
import Button from "../Button/Button"


const NotFound = () => {
    const navigate = useNavigate()
    return (
        <div className="flex grow justify-center items-center flex-col gap-2 w-screen h-screen">
            <div className="text-2xl font-bold">404 Página no encontrada</div>
            <div className="text-lg text-gray-500">La página que estás buscando no existe.</div>
            <Button onClick={() => navigate('/')} variant="secondary" className="mt-4">Volver al inicio</Button>
        </div>
    )
}

export default NotFound