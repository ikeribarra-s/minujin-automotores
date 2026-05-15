import { CheckCircle, X } from "lucide-react";
import { useEffect } from "react";

interface SuccessMessageProps {
  message: string;
  onClose: () => void;
}

export default function SuccessMessage({ message, onClose }: SuccessMessageProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-green-50 border border-green-200 rounded-lg shadow-lg px-4 py-3 flex items-center gap-3 max-w-md">
      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
      <p className="text-sm text-green-800 flex-1">{message}</p>
      <button
        onClick={onClose}
        className="text-green-600 hover:text-green-800 transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
