import "./AvgWaitBannerStyles.scss"

const AvgWaitBanner = ({waitTime}: {waitTime: number}) => {
    return (
        <div className="avg-wait-banner">
            <div className="text-[14px] font-medium text-white">Promedio de espera</div>
            <div className="flex flex-col gap-1 flex-grow items-center justify-center">
                <div className="text-[74px] h-[calc(74px*1.2)] font-bold text-white">{waitTime}</div>
                <div className="text-[14px] font-medium text-[rgba(255,255,255,.7)]">min.</div>
            </div>
        </div>
    )
}

export default AvgWaitBanner