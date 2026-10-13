import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
} from "react";

import {
  Bot,
  LoaderCircle,
  MessageCircle,
  MessageSquarePlus,
  Send,
  User,
  X,
} from "lucide-react";

import {
  isAxiosError,
} from "axios";

import {
  useLocation,
} from "react-router-dom";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  sendChatMessage,
} from "../../api/chat";

import "./AgriTwinAssistant.css";


type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
};


const SESSION_KEY =
  "agritwin_chat_session_id";


const WELCOME_MESSAGE =
  `Hola, soy **AgroTwin Assistant**. 🌱

Puedo ayudarte a interpretar el estado de tu parcela, consultar recomendaciones de riego y explicar por qué AgroTwin genera una determinada recomendación.

Puedes preguntarme de forma natural.`;


function createId(): string {

  if (
    typeof crypto.randomUUID ===
    "function"
  ) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random()}`;
}


function createSessionId(): string {

  const existing =
    sessionStorage.getItem(
      SESSION_KEY
    );

  if (existing) {
    return existing;
  }

  const sessionId =
    `agritwin-${createId()}`;

  sessionStorage.setItem(
    SESSION_KEY,
    sessionId
  );

  return sessionId;
}


function getErrorMessage(
  error: unknown,
): string {

  if (isAxiosError(error)) {

    const detail =
      error.response?.data?.detail;

    if (
      typeof detail === "string"
    ) {
      return detail;
    }

    if (!error.response) {
      return (
        "No puedo contactar con el servidor de AgriTwin en este momento."
      );
    }
  }

  return (
    "No pude completar la consulta. Inténtalo nuevamente."
  );
}


export function AgriTwinAssistant() {

  const location =
    useLocation();


  /*
   * Detectamos silenciosamente si el usuario
   * está viendo /parcels/{UUID}.
   */
  const parcelId =
    useMemo(() => {

      const match =
        location.pathname.match(
          /^\/parcels\/([^/]+)\/?$/
        );

      return match
        ? decodeURIComponent(
            match[1]
          )
        : null;

    }, [
      location.pathname,
    ]);

  const [
    activeParcelId,
    setActiveParcelId,
  ] = useState<string | null>(
    parcelId
  );

  const [
    activeParcelName,
    setActiveParcelName,
  ] = useState<string | null>(
    null
  );

  useEffect(() => {

    if (parcelId) {
      setActiveParcelId(
        parcelId
      );
    }

  }, [
    parcelId,
  ]);


  const quickQuestions =
    parcelId
      ? [
          "¿Cómo está mi parcela?",
          "¿Debo regar?",
          "¿Cuánto debería regar?",
          "¿Por qué?",
        ]
      : [
          "¿Qué puedes hacer?",
          "¿Qué es AgroTwin?",
        ];


  const [open, setOpen] =
    useState(false);

  const [input, setInput] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [sessionId, setSessionId] =
    useState(createSessionId);

  const [messages, setMessages] =
    useState<ChatMessage[]>([
      {
        id: "welcome",
        role: "assistant",
        text: WELCOME_MESSAGE,
      },
    ]);

  const endRef =
    useRef<HTMLDivElement | null>(
      null
    );


  useEffect(() => {

    endRef.current?.scrollIntoView({
      behavior: "smooth",
    });

  }, [
    messages,
    loading,
  ]);


  async function sendMessage(
    rawMessage: string,
  ) {

    const message =
      rawMessage.trim();

    if (
      !message ||
      loading
    ) {
      return;
    }

    const userMessage: ChatMessage = {
      id: createId(),
      role: "user",
      text: message,
    };

    setMessages(
      (current) => [
        ...current,
        userMessage,
      ]
    );

    setInput("");
    setLoading(true);

    try {

      const result =
        await sendChatMessage(
          message,
          sessionId,
          {
            parcelId:
              activeParcelId
              ?? parcelId,
          },
        );

      if (result.parcel_id) {

          setActiveParcelId(
            result.parcel_id
          );
        }

        if (result.parcel_name) {

          setActiveParcelName(
            result.parcel_name
          );
        }

      if (
        result.session_id !==
        sessionId
      ) {

        setSessionId(
          result.session_id
        );

        sessionStorage.setItem(
          SESSION_KEY,
          result.session_id
        );
      }

      setMessages(
        (current) => [
          ...current,
          {
            id: createId(),
            role: "assistant",
            text: result.answer,
          },
        ]
      );

    } catch (error) {

      setMessages(
        (current) => [
          ...current,
          {
            id: createId(),
            role: "assistant",
            text:
              getErrorMessage(
                error
              ),
          },
        ]
      );

    } finally {

      setLoading(false);
    }
  }


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {

    event.preventDefault();

    await sendMessage(
      input
    );
  }


  function resetConversation() {

    const newSessionId =
      `agritwin-${createId()}`;

    sessionStorage.setItem(
      SESSION_KEY,
      newSessionId
    );

    setSessionId(
      newSessionId
    );

    setActiveParcelId(
      parcelId
    );

    setActiveParcelName(
      null
    );

    setMessages([
      {
        id: "welcome",
        role: "assistant",
        text: WELCOME_MESSAGE,
      },
    ]);
  }


  return (
    <>

      {open && (

        <section
          className="agritwin-chat"
          aria-label="AgroTwin Assistant"
        >

          <header
            className="agritwin-chat__header"
          >

            <div
              className="agritwin-chat__identity"
            >

              <div
                className="agritwin-chat__avatar"
              >
                <Bot size={20} />
              </div>

              <div>

                <strong>
                  AgroTwin Assistant
                </strong>

                <span>
                  Asistente del gemelo digital
                </span>

              </div>

            </div>


            <div className="agritwin-chat__actions">
              <button
                type="button"
                title="Nueva conversación"
                onClick={resetConversation}
              >
                <MessageSquarePlus size={18} />
              </button>

              <button
                type="button"
                title="Cerrar"
                onClick={() => setOpen(false)}
              >
                <X size={20} />
              </button>
            </div>

          </header>

          {activeParcelName && (
            <div
              className="agritwin-chat__context"
            >
              🌱 Consultando:
              <strong>
                {activeParcelName}
              </strong>
            </div>

          )}

          <div
            className="agritwin-chat__messages"
          >

            {messages.map(
              (message) => (

                <div
                  key={message.id}
                  className={
                    "agritwin-chat__message " +
                    `agritwin-chat__message--${message.role}`
                  }
                >

                  <div
                    className="agritwin-chat__message-icon"
                  >

                    {message.role ===
                    "assistant" ? (
                      <Bot size={17} />
                    ) : (
                      <User size={17} />
                    )}

                  </div>


                  <div
                    className="agritwin-chat__bubble"
                  >

                    {message.role ===
                    "assistant" ? (

                      <ReactMarkdown
                        remarkPlugins={[
                          remarkGfm,
                        ]}
                      >
                        {message.text}
                      </ReactMarkdown>

                    ) : (

                      message.text

                    )}

                  </div>

                </div>
              )
            )}


            {loading && (

              <div
                className="
                  agritwin-chat__message
                  agritwin-chat__message--assistant
                "
              >

                <div
                  className="agritwin-chat__message-icon"
                >
                  <Bot size={17} />
                </div>

                <div
                  className="
                    agritwin-chat__bubble
                    agritwin-chat__loading
                  "
                >
                  <LoaderCircle
                    size={17}
                    className="agritwin-chat__spinner"
                  />

                  Analizando la parcela...
                </div>

              </div>
            )}


            <div ref={endRef} />

          </div>


          {!loading && (

            <div
              className="agritwin-chat__quick"
            >

              {quickQuestions.map(
                (question) => (

                  <button
                    key={question}
                    type="button"
                    onClick={() =>
                      void sendMessage(
                        question
                      )
                    }
                  >
                    {question}
                  </button>

                )
              )}

            </div>

          )}


          <form
            className="agritwin-chat__form"
            onSubmit={
              handleSubmit
            }
          >

            <textarea
              rows={1}
              value={input}
              disabled={loading}
              placeholder={
                parcelId
                  ? "Pregunta sobre esta parcela..."
                  : "Pregunta a AgroTwin..."
              }
              onChange={(event) =>
                setInput(
                  event.target.value
                )
              }
              onKeyDown={(event) => {

                if (
                  event.key ===
                    "Enter" &&
                  !event.shiftKey
                ) {

                  event.preventDefault();

                  event.currentTarget
                    .form
                    ?.requestSubmit();
                }
              }}
            />


            <button
              type="submit"
              disabled={
                loading ||
                !input.trim()
              }
              title="Enviar"
            >
              <Send size={19} />
            </button>

          </form>

        </section>
      )}


      <button
        type="button"
        className="agritwin-chat-toggle"
        aria-label={
          open
            ? "Cerrar AgroTwin Assistant"
            : "Abrir AgroTwin Assistant"
        }
        onClick={() =>
          setOpen(
            (current) => !current
          )
        }
      >

        {open ? (
          <X size={25} />
        ) : (
          <MessageCircle
            size={27}
          />
        )}

      </button>

    </>
  );
}
