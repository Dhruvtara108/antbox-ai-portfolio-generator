from pydantic import BaseModel, ConfigDict, Field


class Experience(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = ""
    company: str = ""
    dates: str = ""
    location: str = ""
    description: str = ""
    evidence: list[str] = Field(default_factory=list)


class Project(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class Skill(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = ""
    evidence: list[str] = Field(default_factory=list)
    source: str = "candidate_evidence"


class Education(BaseModel):
    model_config = ConfigDict(extra="forbid")

    institution: str = ""
    qualification: str = ""
    dates: str = ""
    evidence: list[str] = Field(default_factory=list)


class RoleAlignment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    capability: str = ""
    level: str = ""
    evidence: list[str] = Field(default_factory=list)
    rationale: str = ""


class WorkingStyle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trait: str = ""
    evidence: list[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = ""
    role: str = ""
    location: str = ""
    email: str = ""
    phone: str = ""
    summary: str = ""
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    role_alignment: list[RoleAlignment] = Field(default_factory=list)
    working_style: list[WorkingStyle] = Field(default_factory=list)
