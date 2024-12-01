import { ArrowLeft } from "iconoir-react"
import "./backButtonStyles.scss"

const BackButton = ({ onClick }: { onClick: () => void }) => {
    return (
        <div className="back-button" onClick={onClick}>
            <div className="icon-box">
                <ArrowLeft/>
            </div>
            Back
        </div>
    )
}

export default BackButton