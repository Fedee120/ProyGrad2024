import Navbar from "./Navbar"

const Layout = ({ children }: { children: React.ReactNode }) => {
    return (
        <div className="flex flex-col min-h-[100vh]">
            <Navbar />
            <div className="layout-content-container">
                {children}
            </div>
        </div>
    )
}

export default Layout