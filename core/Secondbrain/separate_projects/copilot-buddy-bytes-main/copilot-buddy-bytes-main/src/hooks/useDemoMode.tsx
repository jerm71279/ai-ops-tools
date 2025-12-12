import { useSearchParams } from "react-router-dom";

export const useDemoMode = () => {
  const [searchParams] = useSearchParams();
  return searchParams.get("preview") === "true";
};
