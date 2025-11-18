import { SignUp } from '@clerk/nextjs'

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">Get Started</h1>
          <p className="text-slate-400">Create your account to use KIIT Assistant</p>
        </div>
        <SignUp 
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "glass border border-electric-blue/30 shadow-glow-blue",
              headerTitle: "text-white",
              headerSubtitle: "text-slate-400",
              socialButtonsBlockButton: "glass border border-electric-blue/30 hover:border-electric-blue/60 text-white",
              socialButtonsBlockButtonText: "text-white font-semibold",
              formButtonPrimary: "bg-gradient-to-r from-electric-blue to-neon-cyan hover:shadow-glow-blue",
              footerActionLink: "text-electric-blue hover:text-neon-cyan",
              identityPreviewText: "text-white",
              identityPreviewEditButton: "text-electric-blue"
            }
          }}
        />
      </div>
    </div>
  )
}
