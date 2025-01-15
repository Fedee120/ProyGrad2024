import Navbar from "./Navbar"

const Layout = ({ children }: { children: React.ReactNode }) => {
    return (
        <div className="flex flex-col min-h-[100vh] w-full">
            <Navbar />
            <div className="layout-content-container w-full">
                {children}
            </div>
        </div>
    )
}

export default Layout