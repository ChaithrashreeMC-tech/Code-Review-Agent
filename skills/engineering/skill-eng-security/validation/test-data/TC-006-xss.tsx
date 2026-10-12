import React from 'react';

export function UserCommentViolation({ rawComment }: { rawComment: string }) {
  // SEC06 Violation: Rendering unescaped user HTML string directly via dangerouslySetInnerHTML
  return <div dangerouslySetInnerHTML={{ __html: rawComment }} />;
}

export function UserCommentSafe({ rawComment }: { rawComment: string }) {
  // SEC06 Safe: Safe standard JSX string auto-escaping
  return <div>{rawComment}</div>;
}

