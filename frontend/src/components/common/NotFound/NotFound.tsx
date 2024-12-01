import { useNavigate } from "react-router-dom"
import Button from "../Button/Button"


const NotFound = () => {
    const navigate = useNavigate()
    return (
        <div className="flex grow justify-center items-center flex-col gap-2 w-screen h-screen">
            <div className="text-2xl font-bold">404 Not Found</div>
            <div className="text-lg text-gray-500">The page you are looking for does not exist.</div>
            <Button onClick={() => navigate('/')} variant="secondary" className="mt-4">Back to Home</Button>
        </div>
    )
}

export default NotFound