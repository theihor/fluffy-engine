(uiop:define-package :src/main
  (:nicknames :main)
  (:use :common-lisp :anaphora
        )
  )

(in-package :src/main)

(defun main ()
  (handler-case
      (sb-ext:with-timeout 300
        (when sb-ext:*posix-argv*
          (let* ((parsed-args (apply-argv:parse-argv* sb-ext:*posix-argv*))
                 (src-file) (tgt-file))
            ;; (format t "~A~%~A~%" parsed-args (alexandria:plist-alist (cdr parsed-args)))
            (mapcar (lambda (p)
                      (let ((o (string (car p)))
                            (v (cdr p)))
                        (cond
                          ((string= "-s" o) (setf src-file v))
                          ((string= "-t" o) (setf tgt-file v)))))
                    (alexandria:plist-alist (cdr parsed-args)))
            ;; (if (and src-file tgt-file)
            ;;     (generate-trace-for-model :reassembly src-file tgt-file :trivial-low)
            ;;     (if src-file
            ;;         (generate-trace-for-model :disassembly src-file nil :trivial-low)
            ;;         (generate-trace-for-model :assembly nil tgt-file :trivial-parallel-low)))
	    )))
    (sb-ext:timeout (c)
      (declare (ignore c))
      nil)
    (error (e)
      (declare (ignore e))
      nil)))



